PACKAGE_VERSION=0.0.1
prefix=/usr
plugin=wconn_aliyun

all:

clean:
	fixme

install:
	install -d -m 0755 "$(DESTDIR)/$(prefix)/lib64/wrtd/plugins"
	cp -r $(plugin) "$(DESTDIR)/$(prefix)/lib64/wrtd/plugins"
	find "$(DESTDIR)/$(prefix)/lib64/wrtd/plugins/$(plugin)" -type f | xargs chmod 644
	find "$(DESTDIR)/$(prefix)/lib64/wrtd/plugins/$(plugin)" -type d | xargs chmod 755

uninstall:
	rm -rf "$(DESTDIR)/$(prefix)/lib64/wrtd/plugins/$(plugin)"

.PHONY: all clean install uninstall
