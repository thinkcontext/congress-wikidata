#!/usr/bin/python

# Import into Wikidata info from https://github.com/unitedstates/congress-legislators
# on members of Congress

import yaml
import pywikibot

class CongWikidata:
    # simple class for interacting with Wikidata
    TEST = True
    wikidata_site = pywikibot.Site("wikidata","wikidata")
    repo = wikidata_site.data_repository()
    sandbox_id = 'Q4115189' # for testing
    opensecrets_prop = 'P2686'
    youtube_channel_prop = 'P2397'
    twitter_prop = 'P2002'
    instagram_prop = 'P2003'
    facebook_prop = 'P2013'
    religion_prop = 'P140'
    gender_prop = 'P21'
    fec_prop = 'P1839'
    # create a claim to be used as the source for the data
    reference_url = 'https://github.com/unitedstates/congress-legislators'
    reference_url_prop = 'P854'
    reference_url_claim = pywikibot.Claim(repo, reference_url_prop)
    reference_url_claim.setTarget(reference_url)
    def item_from_qid(self,qid,TEST=True):
        # retrieve a Wikidata item from a Q id
        if TEST:
            item = pywikibot.ItemPage(self.repo, self.sandbox_id)
        else:
            item = pywikibot.ItemPage(self.repo, qid)
        item.get()
        return item
    def mk_claim(self,item,prop,val):
        # insert the data, in the form of a claim for a property with a source
        if(val and type(val) == type('a') and len(val) == 0):
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

def dict_items(dict):
    d = {}
    for k in dict.keys():
        item = cong.item_from_qid(dict[k],False)
        item.get()
        d[k] = item
    return d

cong = CongWikidata()

religions = {
    'Lutheran': 'Q75809',
    'Catholic': 'Q1841',
    'Baptist': 'Q93191',
    'African Methodist Episcopal': 'Q384121',
    'Christian': 'Q5043',
    'Christian Scientist': 'Q624477',
    'Church of Christ': 'Q3848233',
    'Episcopalian': 'Q682443',
    'Jewish': 'Q9268',
    'Latter Day Saints': 'Q747802',
    'Methodist': 'Q33203',
    'Nazarene': 'Q1189165',
    'Presbyterian': 'Q178169',
    'Protestant': 'Q23540',
    'Roman Catholic': 'Q9592',
    'Seventh Day Adventist': 'Q104319',
    'Southern Baptist': 'Q1351880',
    'United Methodist': 'Q329646',
    'Islam': 'Q432',
    'United Church of Christ': 'Q426316',
    'Congregationalist':'Q1062789',
    'Greek Orthodox': 'Q7970362',
    'Assembly of God': 'Q2422454',
    'Unitarian': 'Q106687'
}
rkeys = religions.keys()
religions = dict_items(religions)
genders = { 'M':'Q6581097', 'F':'Q6581072'}
genders = dict_items(genders)

class Legislator:
    opensecrets = fec = wikidata = religion = gender = False
    def __init__(self,legislator):
        self.data = {}
        self.name = legislator['name']['official_full']
        bio_keys = legislator['bio'].keys()
        id_keys = legislator['id'].keys()
        ids = ['opensecrets','fec','wikidata','bioguide']
        bios = ['religion', 'gender']
        for b in bios:
            if b in bio_keys:
                self.data[b] = legislator['bio'][b]
            else:
                self.data[b] = False
        for i in ids:
            if i in id_keys:
                self.data[i]  = legislator['id'][i]
            else:
                self.data[i] = False

legislators = yaml.safe_load(open('congress-legislators/legislators-current.yaml'))
bio = {} # holds wikidata ids for the social media pass
for legislator in legislators:
    l = Legislator(legislator)
    bio_id = l.data['bioguide']
    if(l.data['wikidata']):
        print l.name,l.data['wikidata'], l.data['opensecrets']
        wikidata_item = cong.item_from_qid(l.data['wikidata'])
        if(wikidata_item):
            bio[bio_id] = l.data['wikidata']
            if l.data['opensecrets']:
                cong.mk_claim(wikidata_item, cong.opensecrets_prop, l.data['opensecrets'])
            if l.data['religion'] and l.data['religion'] in rkeys:
                cong.mk_claim(wikidata_item, cong.religion_prop, religions[l.data['religion']])
            if l.data['gender'] in ('M','F'):
                cong.mk_claim(wikidata_item, cong.gender_prop, genders[l.data['gender']])
            if l.data['fec'] and len(l.data['fec']) > 0:
                for fec in l.data['fec']:
                    print 'fec ' + fec
                    cong.mk_claim(wikidata_item, cong.fec_prop, fec)
        else:
            print "unable to retrieve a wikidata item for: " + l.data['wikidata']
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
