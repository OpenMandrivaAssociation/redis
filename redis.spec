%define _data_dir       %{_var}/lib/%{name}
%define _log_dir        %{_var}/log/%{name}

Name:           redis
Version:        2.2.8
Release:        %mkrel 1
License:        BSD License
Group:          Databases
Summary:        Persistent key-value database
Url:            http://redis.io/
Source:         http://redis.googlecode.com/files/%{name}-%{version}.tar.gz
Source1:        %{name}.logrotate
Source4:        redis.sysconfig
Patch0:         %{name}-initscript.patch
Patch1:         %{name}-conf.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Requires:       netcat
Requires:       logrotate
BuildRequires:  tcl

%description
Redis is an advanced key-value store. It is similar to memcached but the dataset
is not volatile, and values can be strings, exactly like in memcached,
but also lists, sets, and ordered sets. All this data types can be manipulated
with atomic operations to push/pop elements, add/remove elements, perform server
side union, intersection, difference between sets, and so forth. Redis supports
different kind of sorting abilities.

%package doc
Summary:        HTML documentation for redis
Group:          Databases
Requires:       redis = %{version}

%description doc
HTML documentation for redis database.

%prep
%setup -q
%patch0
mv doc html

%build
make PROF="%{optflags}" %{?jobs:-j%jobs}

%install
%{__install} -Dd -m 0755 \
    %{buildroot}%{_initrddir}/ \
    %{buildroot}%{_sysconfdir}/logrotate.d \
    %{buildroot}%{_bindir} \
    %{buildroot}%{_libdir} \
    %{buildroot}%{_sbindir} \
    %{buildroot}%{_log_dir} \
    %{buildroot}%{_data_dir}

%{__install} -m 0755 src/redis-benchmark  %{buildroot}%{_bindir}/redis-benchmark
%{__install} -m 0755 src/redis-cli        %{buildroot}%{_bindir}/redis-cli
%{__install} -m 0755 src/redis-check-dump %{buildroot}%{_bindir}/redis-check-dump
%{__install} -m 0755 src/redis-check-aof  %{buildroot}%{_bindir}/redis-check-aof
%{__install} -m 0755 src/redis-server     %{buildroot}%{_sbindir}/redis-server
%{__install} -m 0640 redis.conf           %{buildroot}%{_sysconfdir}/redis.conf

# init
%{__install} -m 0755 utils/redis_init_script %{buildroot}%{_initrddir}/redis
%{__ln_s} %{_initrddir}/%{name} %{buildroot}%{_sbindir}/rc%{name}

# logrotate
%{__install} -m 0644 %{S:1} \
    %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%check

cat <<EOF
---------------------------------------------------
The test suite often fails to start a server, with 
'child process exited abnormally' -- sometimes it works.
---------------------------------------------------
EOF
make test && true

%clean
rm -rf %{buildroot}

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
%defattr(-,root,root)
%doc 00-RELEASENOTES BUGS CONTRIBUTING COPYING Changelog README TODO
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_bindir}/redis-*
%{_sbindir}/redis-*
%{_sbindir}/rc%{name}
%config(noreplace) %{_initrddir}/redis
%config(noreplace) %attr(0640, %{name}, %{name}) %{_sysconfdir}/redis.conf
%dir %attr(0750, %{name}, %{name}) %{_data_dir}
%dir %attr(0750, %{name}, %{name}) %{_log_dir}

%files doc
%defattr(-,root,root)
%doc html/

