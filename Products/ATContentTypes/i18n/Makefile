DOMAIN = plone
POTFILE = atct-plone.pot
NEWPOTFILE = new-atct-plone.pot
I18NDUDE = i18ndude
POFILES := $(wildcard *.po)
SKINS := `find ../skins -name '*.*pt'`

all: $(POFILES)

$(POFILES): $(POTFILE)
	$(I18NDUDE) sync --pot $< $@

rebuild-pot:
	i18ndude rebuild-pot --pot $(NEWPOTFILE) --create $(DOMAIN) --merge $(POTFILE) $(SKINS)
