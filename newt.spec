%define majver 0.51
%define libname %mklibname %{name} %{majver}
%define libdevel %{libname}-devel

Summary:	A development library for text mode user interfaces
Name:		newt
Version:	0.51.6
Release:	%mkrel 13
License:	LGPL
Group:		System/Libraries
URL:		http://www.mandriva.com/
Source0:	ftp://ftp.redhat.com/pub/redhat/linux/code/newt/newt-%{version}.tar.bz2
Patch0:		newt-gpm-fix.diff
Patch1:		newt-mdkconf.patch
Patch2:		newt-0.51.4-fix-wstrlen-for-non-utf8-strings.patch
Patch3:		newt-0.51.6-do-not-ignore-EARLY-events-in-listbox--and-allow-textbox-to-take-focus.patch
Patch4:		newt-0.51.6-assorted-fixes.patch
BuildRequires:	glibc-static-devel
BuildRequires:	popt-devel
BuildRequires:	python-devel >= 2.2
BuildRequires:	slang-devel
Requires:	slang
Provides:	snack
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root

%description
Newt is a programming library for color text mode, widget based user
interfaces. Newt can be used to add stacked windows, entry widgets, checkboxes,
radio buttons, labels, plain text fields, scrollbars, etc., to text mode user
interfaces.  This package contains a /usr/bin/dialog replacement called
whiptail. Newt is based on the slang library.

%package -n	%{libname}
Summary:	Newt windowing toolkit development files library
Group:		Development/C
Provides:	%{name} = %{version}-%{release}

%description -n %{libname}
Newt is a programming library for color text mode, widget based user
interfaces. Newt can be used to add stacked windows, entry widgets, checkboxes,
radio buttons, labels, plain text fields, scrollbars, etc., to text mode user
interfaces.  This package contains a /usr/bin/dialog replacement called
whiptail. Newt is based on the slang library.

%package -n	%libdevel
Summary:	Newt windowing toolkit development files
Group:		Development/C
Requires:	slang-devel %{libname} = %{version}
Provides:	lib%{name}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{name}-devel

%description -n %libdevel
Newt is a programming library for color text mode, widget based user
interfaces. Newt can be used to add stacked windows, entry widgets, checkboxes,
radio buttons, labels, plain text fields, scrollbars, etc., to text mode user
interfaces.  This package contains a /usr/bin/dialog replacement called
whiptail. Newt is based on the slang library.

Install newt-devel if you want to develop applications which will use newt.

%prep

%setup -q
%patch0 -p0
%patch1 -p0
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%configure --with-gpm-support
%make
%make shared

%install
rm -rf %{buildroot}

install -d %{buildroot}
%makeinstall

ln -snf lib%{name}.so.%{version} %{buildroot}%{_libdir}/lib%{name}.so.%{majver}

rm -rf %{buildroot}%{_libdir}/python{1.5,2.0,2.1,2.2}

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%clean
rm -rf %{buildroot}

%files -n %{libname}
%defattr (-,root,root)
%doc CHANGES
%{_libdir}/libnewt.so.*

%files 
%defattr (-,root,root)
%doc CHANGES COPYING
%{_bindir}/whiptail
%{_libdir}/python%pyver/site-packages/*

%files -n %libdevel
%defattr (-,root,root)
%doc tutorial.sgml
%{_includedir}/newt.h
%{_libdir}/libnewt.a
%{_libdir}/libnewt.so


