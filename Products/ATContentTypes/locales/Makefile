DOMAIN = plone
POTFILE = atct-plone.pot
MANUALPOT = manual.pot
NEWPOTFILE = new-atct-plone.pot
I18NDUDE = i18ndude
#POFILES := $(wildcard *.po)
POFILES := $(find . -name *.po)
SKINS := `find ../skins -name '*.*pt'`

all: $(POFILES)

$(POFILES): $(POTFILE)
	$(I18NDUDE) sync --pot $< $@

rebuild-pot:
	$(I18NDUDE) rebuild-pot --pot $(NEWPOTFILE) --create $(DOMAIN) --merge $(MANUALPOT) $(SKINS)
