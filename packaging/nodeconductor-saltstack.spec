Name: nodeconductor-saltstack
Summary: SaltStack plugin for NodeConductor
Group: Development/Libraries
Version: 0.2.0
Release: 1.el7
License: Copyright 2015 OpenNode LLC.  All rights reserved.
Url: http://nodeconductor.com
Source0: %{name}-%{version}.tar.gz

Requires: nodeconductor > 0.102.2

BuildArch: noarch
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires: python-setuptools

%description
NodeConductor SaltStack allows to manage SaltStack driven infrastructure.

%prep
%setup -q -n %{name}-%{version}

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install --single-version-externally-managed -O1 --root=%{buildroot} --record=INSTALLED_FILES

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES
%defattr(-,root,root)

%changelog
* Thu Jun 30 2016 Jenkins <jenkins@opennodecloud.com> - 0.2.0-1.el7
- New upstream release

* Tue Dec 8 2015 Jenkins <jenkins@opennodecloud.com> - 0.1.3-1.el7
- New upstream release

* Tue Dec 8 2015 Jenkins <jenkins@opennodecloud.com> - 0.1.2-1.el7
- New upstream release

* Fri Oct 30 2015 Juri Hudolejev <juri@opennodecloud.com> - 0.1.1-1.el7
- New upstream release: 0.1.1

* Thu Oct 29 2015 Juri Hudolejev <juri@opennodecloud.com> - 0.1.0-1.el7
- Initial version of the package
