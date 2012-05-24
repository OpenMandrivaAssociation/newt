%define major 0.52
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

%bcond_without diet
%bcond_without uclibc

Summary:	A development library for text mode user interfaces
Name:		newt
Version:	0.52.14
Release:	2
License:	LGPLv2+
Group:		System/Libraries
URL:		https://fedorahosted.org/newt/
Source0:	https://fedorahosted.org/releases/n/e/newt/%{name}-%{version}.tar.gz

Patch1: 	newt-0.52.6-mdvconf.patch
Patch2: 	newt-0.51.4-fix-wstrlen-for-non-utf8-strings.patch
#Patch3: 	newt-0.51.6-assorted-fixes.patch
BuildRequires:	glibc-static-devel
BuildRequires:	popt-devel
BuildRequires:	python-devel >= 2.2
BuildRequires:	slang-devel
%if %{with diet}
BuildRequires:	dietlibc-devel
%endif
%if %{with uclibc}
BuildRequires:	uClibc-devel >= 0.9.33.2-3
%endif

Provides:	python-snack
Provides:	whiptail

%description
Newt is a programming library for color text mode, widget based user
interfaces. Newt can be used to add stacked windows, entry widgets, checkboxes,
radio buttons, labels, plain text fields, scrollbars, etc., to text mode user
interfaces.  This package contains a /usr/bin/dialog replacement called
whiptail. Newt is based on the slang library.

%package -n	%{libname}
Summary:	Newt windowing toolkit development files library
Group:		Development/C
Provides:	lib%{name} = %{version}-%{release}

%description -n %{libname}
This package contains the shared library for %{name}.

%package -n	%{develname}
Summary:	Newt windowing toolkit development files
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{_lib}%{name}0.52-devel

%description -n %{develname}
This package contains the development files for %{name}.

%prep
%setup -q
%apply_patches

%if %{with diet}
mkdir diet
pushd diet
ln -s ../*.[ch] ../newt.spec .
popd
%endif

%if %{with uclibc}
mkdir uclibc
pushd uclibc
ln -s ../*.[ch] ../newt.spec .
popd
%endif

%build
%if %{with diet}
pushd diet
CC="diet gcc" CFLAGS="-Os -g" \
../configure	--without-gpm-support \
		--without-tcl
%make libnewt.a
popd
%endif

%if %{with uclibc}
pushd uclibc
CC="%{uclibc_cc}" CFLAGS="%{uclibc_cflags}" \
../configure	--without-gpm-support \
		--without-tcl
%make libnewt.a
popd
%endif

%configure2_5x \
	--with-gpm-support \
	--without-tcl
%make
%make shared

%install
#install -d %{buildroot}
%makeinstall

%if %{with diet}
install -m644 diet/libnewt.a -D %{buildroot}%{_prefix}/lib/dietlibc/lib-%{_arch}/libnewt.a
%endif

%if %{with uclibc}
install -m644 uclibc/libnewt.a -D %{buildroot}%{_prefix}/uclibc/%{_libdir}/libnewt.a
%endif

ln -snf lib%{name}.so.%{version} %{buildroot}%{_libdir}/lib%{name}.so.%{major}

rm -rf %{buildroot}%{_libdir}/python{1.5,2.0,2.1,2.2}

%find_lang %{name}

%files -f %{name}.lang
%doc CHANGES COPYING
%{_bindir}/whiptail
%{py_platsitedir}/*
%{_mandir}/man1/whiptail.1*

%files -n %{libname}
%{_libdir}/libnewt.so.%{major}*

%files -n %{develname}
%doc tutorial.sgml
%{_includedir}/newt.h
%{_libdir}/libnewt.a
%if %{with diet}
%{_prefix}/lib/dietlibc/lib-%{_arch}/libnewt.a
%endif
%if %{with uclibc}
%{_prefix}/uclibc%{_libdir}/libnewt.a
%endif
%{_libdir}/libnewt.so
%{_libdir}/pkgconfig/libnewt.pc

