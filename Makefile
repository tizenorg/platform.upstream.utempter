NAME=utempter
VERSION=$(shell awk '/^Version:/ { print $$2 }' $(NAME).spec)
RELEASE=$(shell awk '/^Release:/ { print $$2 }' $(NAME).spec)
CVSTAG=r$(subst .,-,$(VERSION))
CVSROOT=$(shell cat CVS/Root)
# major number of the .so lib
SOMAJOR = 0

SHAREDLIB = lib$(NAME).so
SONAME = $(SHAREDLIB).$(SOMAJOR)

CFLAGS = -Wall $(RPM_OPT_FLAGS)

TARGETS = $(NAME) utmp $(SHAREDLIB)

all:	$(TARGETS)

clean:
	rm -f *.so utempter utmp *.os

%.os : %.c
	$(CC) -c $(CFLAGS) -fPIC $< -o $@

%.o : %.c
	$(CC) -c $(CFLAGS) -fpie $< -o $@

utempter: utempter.o
	$(CC) -o $@ -pie $^

install:
	mkdir -p $(RPM_BUILD_ROOT)/usr/sbin
	mkdir -p $(RPM_BUILD_ROOT)/$(LIBDIR)
	mkdir -p $(RPM_BUILD_ROOT)/usr/include
	install -m 4755 utempter $(RPM_BUILD_ROOT)/usr/sbin
	install -m 644 utempter.h $(RPM_BUILD_ROOT)/usr/include
	install -m 644 $(SHAREDLIB) $(RPM_BUILD_ROOT)/$(LIBDIR)/$(SHAREDLIB).$(VERSION)
	ln -sf $(SHAREDLIB).$(VERSION) $(RPM_BUILD_ROOT)/$(LIBDIR)/$(SHAREDLIB)

$(SHAREDLIB): utmpintf.os
	$(CC) -o $@ -shared -Wl,-soname,$(SONAME) $^ -lc

utmpintf.o: utmpintf.c utempter.h

tag:
	cvs tag $(CVSTAG) .

force-tag:
	cvs tag -F $(CVSTAG) .

archive:
	@rm -rf /tmp/$(NAME)-$(VERSION) /tmp/$(NAME)
	@echo $(VERSION)
	@echo $(CVSROOT)
	@echo $(CVSTAG)
	@echo $(NAME)
	@cd /tmp; cvs -d$(CVSROOT) export -r$(CVSTAG) $(NAME)
	@mv /tmp/$(NAME) /tmp/$(NAME)-$(VERSION)
	@dir=$$PWD; cd /tmp; tar cvzf $$dir/$(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)
	@rm -rf /tmp/$(NAME)-$(VERSION)
	@echo "The archive is in $(NAME)-$(VERSION).tar.gz"

srpm-x:
	@echo Creating $(NAME) src.rpm
	@mkdir -p $(HOME)/rpmbuild/$(NAME)-$(VERSION)
	@mv $(NAME)-$(VERSION).tar.* $(HOME)/rpmbuild/$(NAME)-$(VERSION)/
	@cp $(NAME).spec $(HOME)/rpmbuild/$(NAME)-$(VERSION)/
	@pushd $(HOME)/rpmbuild/$(NAME)-$(VERSION) &> /dev/null ; rpmbuild --nodeps -bs $(NAME).spec ; popd &> /dev/null
	@echo SRPM is: $(HOME)/rpmbuild/SRPMS/$(NAME)-$(VERSION)-$(RELEASE).src.rpm
