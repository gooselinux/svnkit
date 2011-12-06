%define svn_revision     5847

%define eclipse_name     eclipse
%define eclipse_base     %{_libdir}/%{eclipse_name}
%define install_loc      %{_datadir}/eclipse/dropins
%define local_dropins    %{install_loc}/svnkit/eclipse
%define local_plugins    %{local_dropins}/plugins
%define local_features   %{local_dropins}/features
%define core_plugin_name org.tmatesoft.svnkit_%{version}
%define core_plugin_dir  %{local_plugins}/%{core_plugin_name}
%define jna_plugin_name  com.sun.jna_3.0.9
%define jna_plugin_dir   %{local_plugins}/%{jna_plugin_name}

Name:           svnkit
Version:        1.3.0
Release:        3%{?dist}
Summary:        Pure Java Subversion client library

Group:          Development/Tools
# License located at http://svnkit.com/license.html
License:        TMate License and ASL 1.1
URL:            http://www.svnkit.com/
# original source located at: http://www.svnkit.com/org.tmatesoft.svn_%{version}.src.zip
# repackaged removing binary dependencies using:
# zip $FILE -d \*.jar
Source0:        org.tmatesoft.svn_%{version}.src-CLEAN.zip
Patch0:         svnkit-1.2.2-dependencies.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#BuildArch:      noarch
# eclipse-pde is not available on other archs
ExclusiveArch: %{ix86} x86_64

BuildRequires:          ant
BuildRequires:          jpackage-utils >= 0:1.6
BuildRequires:          eclipse-pde
Requires:               eclipse-platform

BuildRequires:          subversion-javahl >= 1.5
Requires:               subversion-javahl >= 1.5
BuildRequires:          jna >= 3.0
BuildRequires:          trilead-ssh2 >= 213
Requires:               jna >= 3.0
Requires:               trilead-ssh2 >= 213
Obsoletes:              javasvn <= 1.1.0

%define debug_package %{nil}


%description
SVNKit is a pure Java Subversion client library. You would like to use SVNKit
when you need to access or modify Subversion repository from your Java
application, be it a standalone program, plugin or web application. Being a
pure Java program, SVNKit doesn't need any additional configuration or native
binaries to work on any OS that runs Java.

%package javadoc
Summary:        Javadoc for SVNKit
Group:          Development/Documentation

%description javadoc
Javadoc for SVNKit - Java Subversion client library.

%package -n eclipse-svnkit
Summary:        Eclipse feature for SVNKit
Group:          Development/Tools
Requires:       svnkit = %{version}

%description -n eclipse-svnkit
Eclipse feature for SVNKit - Java Subversion client library.


%prep
%setup -q -n %{name}-src-%{version}.%{svn_revision}
%patch0 -p1

# delete the jars that are in the archive
JAR_files=""
for j in $(find -name \*.jar); do
if [ ! -L $j ] ; then
JAR_files="$JAR_files $j"
fi
done
if [ ! -z "$JAR_files" ] ; then
echo "These JAR files should be deleted and symlinked to system JAR files: $JAR_files"
exit 1
fi
find contrib -name \*.jar -exec rm {} \;

# delete src packages for dependencies
rm contrib/trilead/trileadsrc.zip

# relinking dependencies
ln -s /usr/share/java/svn-javahl.jar contrib/javahl
ln -sf %{_javadir}/jna.jar contrib/jna/jna.jar
ln -sf %{_javadir}/trilead-ssh2.jar contrib/trilead/trilead.jar

# fixing wrong-file-end-of-line-encoding warnings
sed -i 's/\r//' README.txt doc/javadoc/package-list
find doc/javadoc -name \*.html -exec sed -i 's/\r//' {} \;


%build
ECLIPSE_HOME=%{eclipse_base} ant

%install
rm -rf $RPM_BUILD_ROOT

# jar
install -d -m 755 $RPM_BUILD_ROOT%{_javadir}
install -m 644 build/lib/%{name}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
install -m 644 build/lib/%{name}-javahl.jar $RPM_BUILD_ROOT%{_javadir}/%{name}-javahl-%{version}.jar

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr doc/javadoc/* \
  $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}

# eclipse
mkdir -p $RPM_BUILD_ROOT%{local_dropins}
cp -R build/eclipse/features $RPM_BUILD_ROOT%{local_dropins}

# extracting plugin jars
mkdir $RPM_BUILD_ROOT%{local_plugins}
unzip build/eclipse/site/plugins/%{jna_plugin_name}.jar -d $RPM_BUILD_ROOT%{jna_plugin_dir}
unzip build/eclipse/site/plugins/%{core_plugin_name}.jar -d $RPM_BUILD_ROOT%{core_plugin_dir}
 
# removing plugin internal jars and sources
rm -f $RPM_BUILD_ROOT%{jna_plugin_dir}/jna.jar
rm -f $RPM_BUILD_ROOT%{core_plugin_dir}/{svnkitsrc.zip,trilead.jar,svnkit.jar,svnkit-javahl.jar}

# main library links
pushd $RPM_BUILD_ROOT%{_javadir}/
ln -s %{name}-%{version}.jar %{name}.jar
ln -s %{name}-javahl-%{version}.jar %{name}-javahl.jar
popd

# We need to setup the symlink because the ant copy task doesn't preserve symlinks
# TODO file a bug about this
ln -s %{_javadir}/svn-javahl.jar $RPM_BUILD_ROOT%{core_plugin_dir}
ln -s %{_javadir}/trilead-ssh2.jar $RPM_BUILD_ROOT%{core_plugin_dir}/trilead.jar
ln -s %{_javadir}/svnkit.jar $RPM_BUILD_ROOT%{core_plugin_dir}
ln -s %{_javadir}/jna.jar $RPM_BUILD_ROOT%{jna_plugin_dir}


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root)
%{_javadir}/*
%doc README.txt changelog.txt


%files -n eclipse-svnkit
%defattr(-,root,root)
%{install_loc}/svnkit


%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}


%changelog
* Mon Feb 15 2010 Daniel Novotny <dnovotny@redhat.com> 1.3.0-3
- no debuginfo package now

* Fri Jan 08 2010 Daniel Novotny <dnovotny@redhat.com> 1.3.0-2
- fixed rpmlint error (file permissions)
- made architecture-specific, because eclipse-pde is not
  available on other architectures than ix86 and x86_64 in RHEL now:
  this fixes build problems

* Fri Jul 24 2009 Alexander Kurtakov <akurtako@redhat.com> 1.3.0-1
- Update to 1.3.0.

* Mon Apr  6 2009 Robert Marcano <robert@marcanoonline.com> - 1.2.3-2
- Rebuild

* Mon Mar 23 2009 Robert Marcano <robert@marcanoonline.com> - 1.2.3-1
- Update to upstream 1.2.3

* Tue Feb 17 2009 Robert Marcano <robert@marcanoonline.com> - 1.2.2-1
- Update to upstream 1.2.2
- New eclipse-svnkit subpackage with eclipse plugin
- GCJ AOT removed

* Sun Sep  7 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1.1.4-4
- fix license tag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.1.4-3
- Autorebuild for GCC 4.3

* Thu Sep 20 2007 Robert Marcano <robert@marcanoonline.com> - 1.1.4-2
- Fix Obsoletes to include javasvn = 1.1.0

* Mon Sep 10 2007 Robert Marcano <robert@marcanoonline.com> - 1.1.4-1
- Update to upstream 1.1.4
- Build for all supported arquitectures 

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 1.1.2-4
- Rebuild for selinux ppc32 issue.

* Mon Jun 18 2007 Robert Marcano <robert@marcanoonline.com> 1.1.2-2
- Package review fixes

* Sun Apr 15 2007 Robert Marcano <robert@marcanoonline.com> 1.1.2-1
- Update to upstream 1.1.2
- Add obsoletes of javasvn

* Tue Feb 06 2007 Robert Marcano <robert@marcanoonline.com> 1.1.1-1
- Rename to svnkit
- Update to SVNKit 1.1.1

* Mon Aug 28 2006 Robert Marcano <robert@marcanoonline.com> 1.1.0-0.3.beta4
- Rebuild

* Thu Aug 03 2006 Robert Marcano <robert@marcanoonline.com> 1.1.0-0.2.beta4
- Fix bad relase tag

* Mon Jul 31 2006 Robert Marcano <robert@marcanoonline.com> 1.1.0-0.beta4
- Update to upstream version 1.1.0.beta4, required by subclipse 1.1.4

* Fri Jul 28 2006 Robert Marcano <robert@marcanoonline.com> 1.0.6-2
- Rebuilt to pick up the changes in GCJ (bug #200490)

* Mon Jun 26 2006 Robert Marcano <robert@marcanoonline.com> 1.0.6-1
- Update to upstream version 1.0.6

* Sun Jun 25 2006 Robert Marcano <robert@marcanoonline.com> 1.0.4-4
- created javadoc subpackage
- dependency changed from ganymed to ganymed-ssh2

* Sun Jun 11 2006 Robert Marcano <robert@marcanoonline.com> 1.0.4-3
- rpmlint fixes and debuginfo generation workaround
- doc files added

* Sun May 28 2006 Robert Marcano <robert@marcanoonline.com> 1.0.4-2
- review updates

* Sun May 07 2006 Robert Marcano <robert@marcanoonline.com> 1.0.4-1
- initial version
