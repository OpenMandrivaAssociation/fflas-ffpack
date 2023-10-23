# This package is arch-specific, because it computes properties of the system
# (such as endianness) and stores them in generated header files.  Hence, the
# files DO vary by platform.  However, there is no actual compiled code, so
# turn off debuginfo generation.
%global debug_package %{nil}
%define _disable_lto 1

Name:           fflas-ffpack
Version:        2.5.0
Release:        1
Summary:        Finite field linear algebra subroutines
# %%{_bindir}/fflasffpack-config is CeCILL-B; other files are LGPLv2+
License:        LGPLv2+ and CeCILL-B
URL:            http://linalg.org/projects/fflas-ffpack
Source0:	https://github.com/linbox-team/fflas-ffpack/releases/download/v%{version}/fflas-ffpack-%{version}.tar.gz


BuildRequires:  libatlas-devel
BuildRequires:  doxygen
BuildRequires:  givaro-devel
BuildRequires:  gmp-devel
BuildRequires:  gomp-devel
BuildRequires:  locales-extra-charsets

# Although there are references to linbox-devel files in this package,
# linbox-devel Requires fflas-ffpack-devel, not the other way around.

%description
The FFLAS-FFPACK library provides functionality for dense linear algebra
over word size prime finite fields.

%package devel
Summary:        Header files for developing with fflas-ffpack
Requires:       libatlas-devel, givaro-devel, gmp-devel

%description devel
The FFLAS-FFPACK library provides functionality for dense linear algebra
over word size prime finite fields.  This package provides the header
files for developing applications that use FFLAS-FFPACK.

%package doc
Summary:        API documentation for fflas-ffpack
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description doc
API documentation for fflas-ffpack.

%prep
%autosetup -p1

# Fix character encodings
for f in AUTHORS TODO; do
  iconv -f iso8859-1 -t utf-8 $f > $f.utf8
  touch -r $f $f.utf8
  mv -f $f.utf8 $f
done

# Fix the FSF's address
for f in `grep -FRl 'Temple Place' .`; do
  sed -i.orig \
    's/59 Temple Place, Suite 330, Boston, MA  02111-1307/51 Franklin Street, Suite 500, Boston, MA  02110-1335/' \
    $f
  touch -r $f.orig $f
  rm -f $f.orig
done

# Adapt to monolithic ATLAS libraries in version 3.10 and later
sed -e 's,-lcblas,-lsatlas,' \
    -e 's,-latlas,-lsatlas,' \
    -e 's,$BLAS_HOME/lib/libcblas\.so,$BLAS_HOME/libsatlas.so,' \
    -e 's,-L${BLAS_HOME}/lib,-L${BLAS_HOME},' \
    -e 's,\(ATLAS_NEEDED2=\).*,\1"ATL",' \
    -i configure

%build
#export CC=gcc
#export CXX=g++
%configure --docdir=%{_docdir}/fflas-ffpack --disable-static --enable-openmp \
  --disable-simd --enable-doc \
  --with-blas-cflags="-I%{_includedir}/atlas" \
  --with-blas-libs="-L%{_libdir}/atlas -lsatlas"
%make_build

# Fix the config file for the monolithic ATLAS libraries
sed -e 's, -lsatlas -lsatlas,-lsatlas,' \
    -e 's,%{_libdir}/atlas/lib,%{_libdir}/atlas,' \
    -i fflas-ffpack-config

# Build the developer documentation, too
cd doc
doxygen DoxyfileDev
cd ..

%install
make install DESTDIR=$RPM_BUILD_ROOT

# Documentation is installed in the wrong place
rm -fr $RPM_BUILD_ROOT%{_prefix}/docs

# Don't want these files in with the HTML files
rm -f doc/fflas-ffpack-html/{AUTHORS,COPYING,INSTALL}


%files devel
%doc AUTHORS ChangeLog COPYING TODO
%{_bindir}/fflas-ffpack-config
%{_includedir}/fflas-ffpack
%{_libdir}/pkgconfig/fflas-ffpack.pc

%files doc
%doc doc/fflas-ffpack.html doc/fflas-ffpack-html doc/fflas-ffpack-dev-html
