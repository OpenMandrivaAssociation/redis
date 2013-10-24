# Check for status of man pages
# http://code.google.com/p/redis/issues/detail?id=202

Name:             redis
Version:          2.6.16
Release:          1
Summary:          A persistent key-value database
Group:            Databases
License:          BSD
URL:              http://redis.io/
Source0:	  http://download.redis.io/releases/%{name}-%{version}.tar.gz
Source1:          %{name}.logrotate
Source2:          %{name}.tmpfiles
Source3:          %{name}.service
BuildRequires:    tcl >= 8.5
Requires(post):   rpm-helper >= 0.24.8-1
Requires(preun):  rpm-helper >= 0.24.8-1

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

%build
for i in $(grep -rl 'tclsh8.5');do sed -i 's/tclsh8.5/tclsh8.6/g' $i;done
export CFLAGS="%optflags"
%make CC=%{__cc}

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

%post
%tmpfiles_create %{name}
%_post_service %{name}

%preun
%_preun_service %{name}

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
