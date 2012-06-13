# TODO: pass rpmldflags
Summary:	MongoDB client shell and tools
Summary(pl.UTF-8):	Powłoka kliencka i narzędzia dla bazy danych MongoDB
Name:		mongodb
Version:	2.0.6
Release:	1
License:	AGPL v3
Group:		Applications/Databases
Source0:	http://downloads.mongodb.org/src/%{name}-src-r%{version}.tar.gz
# Source0-md5:	b3b32fecdcbe8e8068ec2989be9d2da4
Source1:	%{name}.logrotate
Source2:	%{name}.init
Patch0:		config.patch
Patch1:		%{name}-system-libs.patch
Patch2:		%{name}-build.patch
URL:		http://www.mongodb.org/
BuildRequires:	boost-devel >= 1.42
BuildRequires:	libpcap-devel
BuildRequires:	libstdc++-devel >= 6:4.0
BuildRequires:	pcre-cxx-devel
BuildRequires:	pcre-devel
BuildRequires:	readline-devel
BuildRequires:	rpmbuild(macros) >= 1.228
BuildRequires:	scons >= 1.2
BuildRequires:	sed >= 4.0
BuildRequires:	snappy-devel
BuildRequires:	v8-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Mongo (from "huMONGOus") is a schema-free document-oriented database.
It features dynamic profileable queries, full indexing, replication
and fail-over support, efficient storage of large binary data objects,
and auto-sharding.

This package provides the mongo shell, import/export tools, and other
client utilities.

%description -l pl.UTF-8
Mongo (od "huMONGOus") to baza danych zorientowana na dokumenty
pozbawione schematu. Obsługuje dynamicznie profilowane zapytania,
pełne indeksowanie, replikację i fail-over, wydajne składowanie dużych
obiektów danych binarnych oraz automatyczne dzielenie.

Ten pakiet zawiera powłokę mongo, narzędzia do eksportu/importu danych
oraz inne narzędzia klienckie.

%package libs
Summary:	MongoDB client library
Summary(pl.UTF-8):	Biblioteka kliencka MongoDB
Group:		Libraries

%description libs
Mongo (from "huMONGOus") is a schema-free document-oriented database.

This package provides the mongo client library.

%description libs -l pl.UTF-8
Mongo (od "huMONGOus") to baza danych zorientowana na dokumenty
pozbawione schematu.

Ten pakiet zawiera bibliotekę kliencką mongo.

%package devel
Summary:	Header files for MongoDB client library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki klienckiej MongoDB
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Mongo (from "huMONGOus") is a schema-free document-oriented database.

This package provides the header files needed to develop MongoDB
client software.

%description devel -l pl.UTF-8
Mongo (od "huMONGOus") to baza danych zorientowana na dokumenty
pozbawione schematu.

Ten pakiet zawiera pliki nagłówkowe potrzebne do tworzenia
oprogramowania klienckiego dla MongoDB.

%package static
Summary:	Static MongoDB client library
Summary(pl.UTF-8):	Statyczna biblioteka kliencka MongoDB
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description static
Mongo (from "huMONGOus") is a schema-free document-oriented database.

This package provides the MongoDB static client library.

%description static -l pl.UTF-8
Mongo (od "huMONGOus") to baza danych zorientowana na dokumenty
pozbawione schematu.

Ten pakiet zawiera statyczną bibliotekę kliencką MongoDB.

%package server
Summary:	MongoDB server, sharding server, and support scripts
Summary(pl.UTF-8):	Serwer MongoDB, serwer dzielący oraz skrypty pomocnicze
Group:		Applications/Databases
Requires:	%{name} = %{version}-%{release}
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Provides:	group(mongod)
Provides:	user(mongod)
Conflicts:	logrotate < 3.8.0

%description server
Mongo (from "huMONGOus") is a schema-free document-oriented database.

This package provides the mongo server software, mongo sharding server
software, default configuration files, and init.d scripts.

%description server -l pl.UTF-8
Mongo (od "huMONGOus") to baza danych zorientowana na dokumenty
pozbawione schematu.

Ten pakiet zawiera serwer mongo, serwer dzielący, pliki domyślnej
konfiguracji oraz skrypty init.d.

%prep
%setup -q -n %{name}-src-r%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%{__sed} -i -e 's,-O3,%{rpmcxxflags} %{rpmcppflags},' SConstruct

# Fix permissions
find -type f -executable | xargs chmod a-x

# force system pcre/js/snappy
%{__rm} -r third_party/{js-1.7,pcre-7.4,snappy,*.py}

%build
%scons \
	--prefix=$RPM_BUILD_ROOT%{_prefix} \
	--sharedclient \
	--full all \
	--usev8 \
	--cxx=%{__cxx}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_mandir}/man1} \
	$RPM_BUILD_ROOT/etc/{logrotate.d,rc.d/init.d,sysconfig} \
	$RPM_BUILD_ROOT%{_var}/{lib,log}/mongo

# XXX: scons is so great, recompiles everything here!
%scons install \
	--prefix=$RPM_BUILD_ROOT%{_prefix} \
	--sharedclient \
	--full \
	--usev8 \
	--cxx=%{__cxx}

cp -p %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/mongod
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/mongod
cp -p rpm/mongod.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/mongod
cp -p rpm/mongod.conf $RPM_BUILD_ROOT%{_sysconfdir}/mongod.conf
cp -p debian/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

touch $RPM_BUILD_ROOT%{_var}/log/mongo/mongod.log

%clean
rm -rf $RPM_BUILD_ROOT

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%pre server
%groupadd -g 258 -r mongod
%useradd -u 258 -r -g mongod -d %{_var}/lib/mongo -s /bin/false -c "MongoDB Database Server" mongod

%post server
/sbin/chkconfig --add mongod
%service mongod restart

%preun server
if [ "$1" = "0" ]; then
	%service -q mongod stop
	/sbin/chkconfig --del mongod
fi

%postun server
if [ "$1" = "0" ]; then
	%userremove mongod
	%groupremove mongod
fi

%files
%defattr(644,root,root,755)
%doc README GNU-AGPL-3.0.txt
%attr(755,root,root) %{_bindir}/bsondump
%attr(755,root,root) %{_bindir}/mongo
%attr(755,root,root) %{_bindir}/mongodump
%attr(755,root,root) %{_bindir}/mongoexport
%attr(755,root,root) %{_bindir}/mongofiles
%attr(755,root,root) %{_bindir}/mongoimport
%attr(755,root,root) %{_bindir}/mongorestore
%attr(755,root,root) %{_bindir}/mongosniff
%attr(755,root,root) %{_bindir}/mongostat
%attr(755,root,root) %{_bindir}/mongotop
%{_mandir}/man1/bsondump.1*
%{_mandir}/man1/mongo.1*
%{_mandir}/man1/mongodump.1*
%{_mandir}/man1/mongoexport.1*
%{_mandir}/man1/mongofiles.1*
%{_mandir}/man1/mongoimport.1*
%{_mandir}/man1/mongosniff.1*
%{_mandir}/man1/mongostat.1*
%{_mandir}/man1/mongorestore.1*

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libmongoclient.so

%files devel
%defattr(644,root,root,755)
%{_includedir}/mongo

%files static
%defattr(644,root,root,755)
%{_libdir}/libmongoclient.a

%files server
%defattr(644,root,root,755)
%dir %{_sysconfdir}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/mongod.conf
%attr(754,root,root) /etc/rc.d/init.d/mongod
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/mongod
%config(noreplace) /etc/logrotate.d/mongod
%attr(755,root,root) %{_bindir}/mongod
%attr(755,root,root) %{_bindir}/mongos
%{_mandir}/man1/mongod.1*
%{_mandir}/man1/mongos.1*
%attr(755,mongod,mongod) %dir %{_var}/lib/mongo
%attr(755,mongod,mongod) %dir %{_var}/log/mongo
%attr(640,mongod,mongod) %config(noreplace) %verify(not md5 mtime size) %{_var}/log/mongo/mongod.log
