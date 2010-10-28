# TODO
# - pld useradd/groupadd (register uid/gid)
Summary:	MongoDB client shell and tools
Name:		mongodb
Version:	1.6.2
Release:	0.1
License:	AGPL 3.0
Group:		Applications/Databases
URL:		http://www.mongodb.org/
Source0:	http://downloads.mongodb.org/src/%{name}-src-r%{version}.tar.gz
# Source0-md5:	358bfc52855a66d3c954e7f6f51bcd12
Source1:	%{name}.logrotate
Source2:	%{name}.init
# BuildRequires:  libpcap-devel
BuildRequires:	boost-devel >= 1.42
BuildRequires:	gcc >= 6:4.0
BuildRequires:	libstdc++-devel
BuildRequires:	libstdc++-devel >= 4.0
BuildRequires:	pcre-cxx-devel
BuildRequires:	pcre-devel
BuildRequires:	readline-devel
BuildRequires:	scons >= 1.2
BuildRequires:	v8-devel
Requires:	libstdc++
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Requires(pre):	pwdutils

%description
Mongo (from "huMONGOus") is a schema-free document-oriented database.
It features dynamic profileable queries, full indexing, replication
and fail-over support, efficient storage of large binary data objects,
and auto-sharding.

This package provides the mongo shell, import/export tools, and other
client utilities.

%package server
Summary:	MongoDB server, sharding server, and support scripts
Group:		Applications/Databases
Requires:	%{name} = %{version}
Requires:	logrotate

%description server
Mongo (from "huMONGOus") is a schema-free document-oriented database.

This package provides the mongo server software, mongo sharding server
softwware, default configuration files, and init.d scripts.

%package devel
Summary:	Headers and libraries for mongo development
Group:		Development/Libraries
Requires:	%{name} = %{version}

%description devel
Mongo (from "huMONGOus") is a schema-free document-oriented database.

This package provides the mongo static library and header files needed
to develop mongo client software.

%prep
%setup -q -n %{name}-src-r%{version}

# Fix permissions
find -type f -executable | xargs chmod a-x

%build
%scons \
	--prefix=$RPM_BUILD_ROOT%{_prefix} \
	--sharedclient \
	--full all \
	--usev8

# XXX really should have shared library here

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_mandir}/man1} \
	$RPM_BUILD_ROOT/etc/{logrotate.d,rc.d/init.d} \
	$RPM_BUILD_ROOT%{_var}/{lib,log}/mongo
%scons install \
	--prefix=$RPM_BUILD_ROOT%{_prefix} \
	--sharedclient \
	--full \
	--usev8

cp -a debian/*.1 $RPM_BUILD_ROOT%{_mandir}/man1
#install -d $RPM_BUILD_ROOT%{_sysconfdir}/init.d
#cp rpm/init.d-mongod $RPM_BUILD_ROOT%{_sysconfdir}/init.d/mongod
#chmod a+x $RPM_BUILD_ROOT%{_sysconfdir}/init.d/mongod

cp -a rpm/mongod.conf $RPM_BUILD_ROOT%{_sysconfdir}/mongod.conf
#install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
#cp rpm/mongod.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/mongod
#cp rpm/mongod.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/mongod

touch $RPM_BUILD_ROOT%{_var}/log/mongo/mongod.log
cp -a %{SOURCE1} $RPM_BUILD_ROOT/etc/logrotate.d/mongod
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/mongod

#install -d $RPM_BUILD_ROOT%{_sbindir}
#ln -s %{_sysconfdir}/init.d/mongod $RPM_BUILD_ROOT%{_sbindir}/rcmongod
# XXX PFF?
ln -s ../../etc/rc.d/init.d/mongod $RPM_BUILD_ROOT%{_sbindir}/rcmongod

%clean
rm -rf $RPM_BUILD_ROOT

%pre server
groupadd -r mongod 2>/dev/null || :
useradd -r -g mongod -d %{_var}/lib/mongo -s /sbin/nologin -c "user for MongoDB Database Server" mongod 2>/dev/null || :

%post server
#%fillup_and_insserv -n mongod mongod
#%restart_on_update mongod

%preun server
#%stop_on_removal mongod

%postun server

%post	devel -p /sbin/ldconfig
%postun	devel -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README GNU-AGPL-3.0.txt
%attr(755,root,root) %{_bindir}/mongo
%attr(755,root,root) %{_bindir}/mongodump
%attr(755,root,root) %{_bindir}/mongoexport
%attr(755,root,root) %{_bindir}/mongofiles
%attr(755,root,root) %{_bindir}/mongoimport
%attr(755,root,root) %{_bindir}/mongorestore
%attr(755,root,root) %{_bindir}/mongostat
%attr(755,root,root) %{_bindir}/bsondump
%{_mandir}/man1/mongo.1*
%{_mandir}/man1/mongod.1*
%{_mandir}/man1/mongodump.1*
%{_mandir}/man1/mongoexport.1*
%{_mandir}/man1/mongofiles.1*
%{_mandir}/man1/mongoimport.1*
%{_mandir}/man1/mongosniff.1*
%{_mandir}/man1/mongostat.1*
%{_mandir}/man1/mongorestore.1*

%files server
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/mongod.conf
%config(noreplace) /etc/logrotate.d/mongod
%attr(754,root,root) %config /etc/rc.d/init.d/mongod
%attr(755,root,root) %{_sbindir}/rcmongod
%config %{_var}/adm/fillup-templates/sysconfig.mongod
%attr(755,root,root) %{_bindir}/mongod
%attr(755,root,root) %{_bindir}/mongos
%{_mandir}/man1/mongos.1*
%attr(755,mongod,mongod) %dir %{_var}/lib/mongo
%attr(755,mongod,mongod) %dir %{_var}/log/mongo
%attr(640,mongod,mongod) %config(noreplace) %verify(not md5 mtime size) %{_var}/log/mongo/mongod.log

%files devel
%defattr(644,root,root,755)
%{_includedir}/mongo
%{_libdir}/libmongoclient.a
%{_libdir}/libmongoclient.so
#%{_libdir}/libmongotestfiles.a
