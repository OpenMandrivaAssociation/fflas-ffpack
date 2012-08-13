# This package is arch-specific, because it computes properties of the system
# (such as endianness) and stores them in generated header files.  Hence, the
# files DO vary by platform.  However, there is no actual compiled code, so
# turn off debuginfo generation.
%global debug_package %{nil}

Name:           fflas-ffpack
Version:        1.6.0
Release:        1
Summary:        Finite field linear algebra subroutines

Group:          Sciences/Mathematics
# %%{_bindir}/fflasffpack-config is CeCILL-B; other files are LGPLv2+
License:        LGPLv2+ and CeCILL-B
URL:            http://linalg.org/projects/fflas-ffpack
Source0:        http://linalg.org/%{name}-%{version}.tar.gz

# Patch from upstream discussion list.  Fixes building with debug.
Patch1:         %{name}-debug.patch

BuildRequires:  libatlas-devel
BuildRequires:  doxygen
BuildRequires:  givaro-devel
BuildRequires:  gmp-devel
BuildRequires:  gomp-devel
BuildRequires:  texlive

# Although there are references to linbox-devel files in this package,
# linbox-devel Requires fflas-ffpack-devel, not the other way around.

%description
The FFLAS-FFPACK library provides functionality for dense linear algebra
over word size prime finite fields.

%package devel
Summary:        Header files for developing with fflas-ffpack
Group:          Development/C++
Requires:       libatlas-devel, givaro-devel, gmp-devel

%description devel
The FFLAS-FFPACK library provides functionality for dense linear algebra
over word size prime finite fields.  This package provides the header
files for developing applications that use FFLAS-FFPACK.

%prep
%setup -q
%patch1 -p1

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

%build
%configure --docdir=%{_docdir}/fflas-ffpack-%{version} --disable-static \
  --enable-optimization --enable-doc --with-cblas=%{_libdir}/atlas \
  --with-lapack=%{_libdir}/atlas
make %{?_smp_mflags}

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

%check
make check

%files devel
%doc AUTHORS ChangeLog COPYING README TODO
%{_bindir}/fflas-ffpack-config
%{_includedir}/fflas-ffpack
%doc doc/fflas-ffpack.html doc/fflas-ffpack-html doc/fflas-ffpack-dev-html
