#!/usr/bin/python

# Import into Wikidata info from https://github.com/unitedstates/congress-legislators
# on members of Congress

import yaml
import pywikibot

class CongWikidata:
    # simple class for interacting with Wikidata
    TEST = False
    wikidata_site = pywikibot.Site("wikidata","wikidata")
    repo = wikidata_site.data_repository()
    sandbox_id = 'Q4115189' # for testing
    opensecrets_prop = 'P2686'
    youtube_channel_prop = 'P2397'
    twitter_prop = 'P2002'
    instagram_prop = 'P2003'
    facebook_prop = 'P2013'
    # create a claim to be used as the source for the data
    reference_url = 'https://github.com/unitedstates/congress-legislators'
    reference_url_prop = 'P854'
    reference_url_claim = pywikibot.Claim(repo, reference_url_prop)
    reference_url_claim.setTarget(reference_url)
    def item_from_qid(self,qid):
        # retrieve a Wikidata item from a Q id
        if self.TEST:
            item = pywikibot.ItemPage(self.repo, self.sandbox_id)
        else:
            item = pywikibot.ItemPage(self.repo, qid)
        item.get()
        return item
    def mk_claim(self,item,prop,val):
        # insert the data, in the form of a claim for a property with a source
        if(len(val) == 0):
            print 'val has no length'
            return False
        claims = item.claims.keys()
        if prop in claims:
            print 'already have ' + prop
        else:
            claim = pywikibot.Claim(self.repo, prop)
            claim.setTarget(val)
            item.addClaim(claim)
            claim.addSource(self.reference_url_claim)

cong = CongWikidata()
legislators = yaml.safe_load(open('congress-legislators/legislators-current.yaml'))
bio = {} # holds wikidata ids for the social media pass
for legislator in legislators:
    bio_id = legislator['id']['bioguide']
    wikidata = legislator['id']['wikidata']
    opensecrets = legislator['id']['opensecrets']
    if(wikidata):
        print legislator['name']['official_full'],wikidata, opensecrets
        wikidata_item = cong.item_from_qid(wikidata)
        if(wikidata_item):
            bio[bio_id] = legislator['id']['wikidata']
            if opensecrets:
                cong.mk_claim(wikidata_item, cong.opensecrets_prop, opensecrets)
        else:
            print "unable to retrieve a wikidata item for: " + wikidata
    else:
        print "no wikidata id present for: " + bio_id
bkeys = bio.keys()
social = yaml.safe_load(open('congress-legislators/legislators-social-media.yaml'))
for s in social:
    facebook = twitter = youtube_channel_id = instagram = False
    bio_id = s['id']['bioguide']
    print bio_id
    if bio_id and (bio_id in bkeys):
        wikidata_item = cong.item_from_qid(bio[bio_id])
        if wikidata_item:
            skeys = s['social'].keys()
            if 'youtube_id' in skeys:
                youtube_channel_id = s['social']['youtube_id']
                cong.mk_claim(wikidata_item, cong.youtube_channel_prop, youtube_channel_id)
            if 'facebook' in skeys:
                facebook = s['social']['facebook']
                cong.mk_claim(wikidata_item, cong.facebook_prop, facebook)
            if 'twitter' in skeys:
                twitter = s['social']['twitter']
                cong.mk_claim(wikidata_item, cong.twitter_prop, twitter)
            if 'instagram' in skeys:
                instagram = s['social']['instagram']
                cong.mk_claim(wikidata_item, cong.instagram_prop, instagram)
    else:
        print 'non current bio_id found: ' + bio_id
