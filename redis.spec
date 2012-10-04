# Check for status of man pages
# http://code.google.com/p/redis/issues/detail?id=202

Name:             redis
Version:          2.4.17
Release:          %mkrel 1
Summary:          A persistent key-value database

Group:            Databases
License:          BSD
URL:              http://redis.io/
Source0:          http://redis.googlecode.com/files/%{name}-%{version}.tar.gz
Source1:          %{name}.logrotate
Source2:          %{name}.tmpfiles
Source3:          %{name}.service
# Update configuration for Fedora
Patch0:           %{name}-2.0.0-redis.conf.patch
Patch1:		  redis-2.4.8-extend-timeout-on-replication-test.patch
Patch2:           redis-2.4.17-tcl86.patch
BuildRequires:    tcl >= 8.6
Requires(post):   rpm-helper >= 0.24.1-1
Requires(preun):  rpm-helper >= 0.24.1-1

%description
Redis is an advanced key-value store.
It is similar to memcached but the data set is not
volatile, and values can be strings, exactly like in
memcached, but also lists, sets, and ordered sets.
All this data types can be manipulated with atomic operations
to push/pop elements, add/remove elements, perform server side
union, intersection, difference between sets, and so forth.
Redis supports different kind of sorting abilities.

%prep
%setup -q
%patch0 -p0
%patch1 -p1
%patch2 -p1
# Remove integration tests
sed -i '/    execute_tests "integration\/replication"/d' tests/test_helper.tcl
sed -i '/    execute_tests "integration\/aof"/d' tests/test_helper.tcl

%build
export LC_ALL=C
%make -j1 DEBUG="" CFLAGS='%{optflags} -std=c99' all FORCE_LIBC_MALLOC=yes

%check
tclsh tests/test_helper.tcl

%install
# Install binaries
install -p -D -m 755 src/%{name}-benchmark %{buildroot}%{_bindir}/%{name}-benchmark
install -p -D -m 755 src/%{name}-cli %{buildroot}%{_bindir}/%{name}-cli
install -p -D -m 755 src/%{name}-check-aof %{buildroot}%{_bindir}/%{name}-check-aof
install -p -D -m 755 src/%{name}-check-dump %{buildroot}%{_bindir}/%{name}-check-dump
install -p -D -m 755 src/%{name}-server %{buildroot}%{_sbindir}/%{name}-server
# Install misc other
install -d -m 755 %{buildroot}%{_sysconfdir}
install -m 644 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf
install -d -m 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -d -m 755 %{buildroot}%{_prefix}/lib/tmpfiles.d
install -m 755 %{SOURCE2} %{buildroot}%{_prefix}/lib/tmpfiles.d/%{name}.conf
install -d -m 755 %{buildroot}%{_unitdir}
install -m 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service

install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{name}


%pre
%_pre_useradd redis  %{_sharedstatedir}/redis /sbin/nologin

%post
systemd-tmpfiles --create %{name}.conf
%_post_service redis

%preun
%_preun_service redis

%postun
%_postun_userdel redis

%files
%doc 00-RELEASENOTES BUGS COPYING README
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%dir %attr(0755, redis, root) %{_localstatedir}/lib/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/log/%{name}
%{_bindir}/%{name}-*
%{_sbindir}/%{name}-*
%{_prefix}/lib/tmpfiles.d/%{name}.conf
%{_unitdir}/%{name}.service
