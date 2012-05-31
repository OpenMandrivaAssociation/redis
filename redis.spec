%define _data_dir       %{_var}/lib/%{name}
%define _log_dir        %{_var}/log/%{name}

Name:		redis
Version:	2.4.14
Release:	%mkrel 1
License:	BSD License
Group:		Databases
Summary:	Persistent key-value database
Url:		http://redis.io/
Source0:	http://redis.googlecode.com/files/%{name}-%{version}.tar.gz
Requires:	netcat
Patch0:		%{name}-2.4.6-redis.conf.patch
Source1:	%{name}.logrotate
Source2:	%{name}.init
Source3:	%{name}.service

Requires:	logrotate
BuildRequires:	tcl

%description
Redis is an advanced key-value store.
It is similar to memcached but the dataset
is not volatile, and values can be 
strings, exactly like in memcached,
but also lists, sets, and ordered sets.
All this data types can be manipulated
with atomic operations to push/pop elements,
add/remove elements, perform server
side union, intersection, difference between
sets, and so forth. Redis supports
different kind of sorting abilities.

%prep
%setup -q
%patch0 -p1

%build
%make  all



%check

cat <<EOF
---------------------------------------------------
The test suite often fails to start a server, with 
'child process exited abnormally' -- sometimes it works.
---------------------------------------------------
EOF
make test && true


%install
make install PREFIX=%{buildroot}%{_prefix}
# Install misc other
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -p -D -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}
install -p -D -m 644 %{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf
install -d -m 755 %{buildroot}%{_localstatedir}/lib/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{name}
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{name}
# Install systemd unit
install -p -D -m 644 %{SOURCE3} %{buildroot}/%{_unitdir}/%{name}.service

# Fix non-standard-executable-perm error
chmod 755 %{buildroot}%{_bindir}/%{name}-*

# Ensure redis-server location doesn't change
mkdir -p %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/%{name}-server %{buildroot}%{_sbindir}/%{name}-server

#==========================================================
%pre
/usr/sbin/groupadd -r %{name} &>/dev/null || :
/usr/sbin/useradd -o -g %{name} -s /bin/false -r -c "User for Redis key-value store" -d %{_data_dir} %{name} &>/dev/null || :

%post
%_post_service %{name}
echo "To start the database server, do:"
echo " sudo rcredis start; insserv redis"

%preun
%_preun_service %{name}

%files
%doc 00-RELEASENOTES BUGS CONTRIBUTING COPYING README
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%dir %attr(0755, redis, root) %{_localstatedir}/lib/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/log/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/run/%{name}
%{_bindir}/%{name}-*
%{_sbindir}/%{name}-*
%{_initrddir}/%{name}
%{_unitdir}/%{name}.service
