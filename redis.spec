# Check for status of man pages
# http://code.google.com/p/redis/issues/detail?id=202

Name:		redis
Version:	2.8.13
Release:	1
Summary:	A persistent key-value database
Group:		Databases
License:	BSD
URL:		http://redis.io/
Patch0:		redis-2.8.3-config.patch
Patch1:		redis-2.8.3-shared.patch
Source0:	http://download.redis.io/releases/%{name}-%{version}.tar.gz
Source1:	redis.logrotate
Source2:	redis.tmpfiles
Source3:	redis.service
BuildRequires:	tcl >= 8.5
BuildRequires:	jemalloc-devel
Requires(pre):	rpm-helper >= 0.24.8-1
Requires(postun):rpm-helper >= 0.24.8-1

%description
Redis is an advanced key-value store.
It is similar to memcached but the data set is not volatile,
and values can be strings, exactly like in memcached,
but also lists, sets, and ordered sets.
All this data types can be manipulated with atomic operations
to push/pop elements, add/remove elements, perform server side
union, intersection, difference between sets, and so
forth. Redis supports different kind of sorting abilities.

%prep
%setup -q
%apply_patches
sed -i -e 's:AR=:AR?=:g' -e 's:RANLIB=:RANLIB?=:g' deps/lua/src/Makefile
sed -i -e "s:-std=c99::g" deps/linenoise/Makefile deps/Makefile

%build
%make CC="%{__cc}" CFLAGS="%{optflags}" AR="%{__ar} rcu" JEMALLOC_SHARED=yes

%check
tclsh tests/test_helper.tcl

%install
# Install binaries
install -p -D -m 0755 src/%{name}-benchmark %{buildroot}%{_bindir}/%{name}-benchmark
install -p -D -m 0755 src/%{name}-cli %{buildroot}%{_bindir}/%{name}-cli
install -p -D -m 0755 src/%{name}-check-aof %{buildroot}%{_bindir}/%{name}-check-aof
install -p -D -m 0755 src/%{name}-check-dump %{buildroot}%{_bindir}/%{name}-check-dump
install -p -D -m 0755 src/%{name}-server %{buildroot}%{_sbindir}/%{name}-server
# Install misc other
install -p -D -m 0644 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf
install -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -p -D -m 0755 %{SOURCE2} %{buildroot}%{_tmpfilesdir}/%{name}.conf
install -p -D -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service

install -d -m 0755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m 0755 %{buildroot}%{_localstatedir}/log/%{name}

%pre
%_pre_useradd %{name}  %{_sharedstatedir}/%{name} /sbin/nologin

%postun 
%_postun_userdel %{name}

%files
%doc 00-RELEASENOTES BUGS COPYING README
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%dir %attr(0755, redis, root) %{_localstatedir}/lib/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/log/%{name}
%{_bindir}/%{name}-*
%{_sbindir}/%{name}-*
%{_tmpfilesdir}/%{name}.conf
%{_unitdir}/%{name}.service
