from PyPoE.poe.file import dat
from PyPoE.poe.file.ggpk import GGPKFile
from PyPoE.poe.file.translations import TranslationFileCache
from PyPoE.poe.sim import mods
import operator


def load_from_ggpk():
	ggpk = GGPKFile()
	ggpk.read(r'C:\Games\Grinding Gear Games\Path of Exile\content.ggpk')
	ggpk.directory_build()
	r = dat.RelationalReader(path_or_ggpk=ggpk, files=['CraftingBenchOptions.dat'], read_options={'use_dat_value': False})
	tc = TranslationFileCache(path_or_ggpk=ggpk, files=['stat_descriptions.txt'], merge_with_custom_file=True)
	#
	ret = []
	for i in r['CraftingBenchOptions.dat'].row_iter():
		# if item is from prophecy, Default/plinth, niko, jun
		if i['HideoutNPCsKey'].rowid in [0, 3, 4, 5]:
			temp = {
				'name': mods.get_translation(i['ModsKey'], tc, use_placeholder=True).lines if i['ModsKey'] else [i['RecipeIds'][0]['Description']] if i['RecipeIds'] else ['Default'],
				'mod': mods.get_translation(i['ModsKey'], tc).lines if i['ModsKey'] else [i['Name']] if i['Name'] else ['Default'],
				'master': 9 if i['HideoutNPCsKey'].rowid == 0 else 1 if i['HideoutNPCsKey'].rowid == 4 else i['HideoutNPCsKey'].rowid,  # ['Hideout_NPCsKey']['Name'],
				'mod_group_name': i['ModFamily'] if i['ModFamily'] else [i['RecipeIds'][0]['Description']] if i['RecipeIds'] else ['Default'],
				'order': i['Order'],
				'tier': i['Tier'],
				'cost': i['Cost_Values'],
				'currency': [j['Name'] for j in i['Cost_BaseItemTypesKeys']],
				'bases': [j['Id'] for j in i['CraftingItemClassCategoriesKeys']],
				'location': i['CraftingBenchUnlockCategoriesKey']['ObtainingDescription'] if i['CraftingBenchUnlockCategoriesKey'] is not None else i['RecipeIds'][0]['UnlockDescription'] if i['RecipeIds'] else 'Default',
				'groupid': i['CraftingBenchUnlockCategoriesKey'].rowid if i['CraftingBenchUnlockCategoriesKey'] is not None else i['RecipeIds'][0]['RecipeId'] if i['RecipeIds'] else 'default',
				'type': i['AffixType']
			}
			ret.append(temp)
	ret = sorted(ret, key=operator.itemgetter('master', 'order', 'tier'))
	return ret


# Helper function for Jun veiled names
def parse_jun(loc, type):
	# For converting veiled
	veillookup = {
		'Gravicius Reborn': "Gravicius' Veiled",
		'Rin Yuushu': "Rin's Veiled",
		'Guff Grenn': "Guff's Veiled",
		'Vorici': "Vorici's Veiled",
		'Korell Goya': "Korell's Veiled",
		'Vagan': "Vagan's Veiled",
		'Elreon': "Elreon's Veiled",
		'Leo': "Leo's Veiled",
		'Tora': "Tora's Veiled",
		'Haku': "Haku's Veiled",
		'It That Fled': "It That Fled's Veiled",
		'Syndicate Mastermind': "Catarina's Veiled",

		'Thane Jorgin': "of Jorgin's Veil",
		'Hillock, the Blacksmith': "of Hillock's Veil",
		'Janus Perandus': "of Janus' Veil",
		'Aisling Laffrey': "of Aisling's Veil",
		'Cameria the Coldblooded': "of Cameria's Veil",
		'Riker Maloney': "of Riker's Veil",
	}
	for i in veillookup:
		if i in loc:
			return veillookup[i]
	if type == 'Prefix':
		return 'Veiled'
	return 'of the Veil'


# given a sorted list of dictionaries representing recipes, clean up the data for presentation
def htmlify(data):
	# For converting currencies and bases to images
	spanlookup = {
		"Orb of Alteration": 'alt',
		"Orb of Transmutation": 'transmute',
		"Orb of Alchemy": 'alch',
		"Chaos Orb": 'chaos',
		"Orb of Augmentation": 'aug',
		"Orb of Chance": 'chance',
		"Divine Orb": 'divine',
		"Exalted Orb": 'exalt',
		"Regal Orb": 'regal',
		"Glassblower's Bauble": 'bauble',
		"Vaal Orb": 'vaal',
		"Armourer's Scrap": 'scrap',
		"Blessed Orb": 'blessed',
		"Orb of Fusing": 'fuse',
		"Jeweller's Orb": 'jorb',
		"Chromatic Orb": 'chrom',
		"Orb of Scouring": 'scour',
		"Gemcutter's Prism": 'gcp',
		"Blacksmith's Whetstone": 'whetstone',

		"OneHandMelee": 'om',
		"OneHandRanged": 'or',
		"TwoHandMelee": 'tm',
		"TwoHandRanged": 'tr',
		"Amulet": 'am',
		"BodyArmour": 'bd',
		"Belt": 'be',
		"Boots": 'bo',
		"Gloves": 'gl',
		"Helmet": 'he',
		"Quiver": 'qu',
		"Ring": 'ri',
		"Shield": 'sh',
		"Flask": 'fl'
	}
	processed = {}
	groups = {}

	for mod in data:
		if mod['type'] not in processed:
			processed[mod['type']] = []
			groups[mod['type']] = []
		name = (mod['mod_group_name'], mod['master'])
		if name in groups[mod['type']]:
			idx = groups[mod['type']].index(name)
		else:
			idx = -1
			groups[mod['type']].append(name)
			processed[mod['type']].append({
				'name': '<br>'.join(mod['name']),
				"mods": {}
			})
		if mod['tier'] in processed[mod['type']][idx]['mods']:
			processed[mod['type']][idx]['mods'][mod['tier']]['name'] += '<br><br>' + '<br>'.join(mod['mod']).replace("'", "\\'")
			cost_ = ', '.join([f'{mod["cost"][i]}<span class="{spanlookup[mod["currency"][i]]}"></span>' for i in range(len(mod['cost']))]).replace("'", "\\'")
			slots_ = ''.join([f'<span class="{spanlookup[i]}"></span>' for i in mod['bases']])
			loc_ = mod['location'].replace("'", "\\'") if mod['master'] != 5 else parse_jun(mod['location'], mod['type']).replace("'", "\\'")
			groupid_ = f"{mod['master']}-{mod['groupid']}"
			if cost_ not in processed[mod['type']][idx]['mods'][mod['tier']]['cost']:
				processed[mod['type']][idx]['mods'][mod['tier']]['cost'] += f"<br><br>{cost_}"
			if slots_ not in processed[mod['type']][idx]['mods'][mod['tier']]['slots']:
				processed[mod['type']][idx]['mods'][mod['tier']]['slots'] += f"<br><br>{slots_}"
				processed[mod['type']][idx]['mods'][mod['tier']]['slots_meta'].update(set([f'{spanlookup[i]}' for i in mod['bases']]))
			if loc_ not in processed[mod['type']][idx]['mods'][mod['tier']]['loc']:
				processed[mod['type']][idx]['mods'][mod['tier']]['loc'] += f"<br><br>{loc_}"
			if groupid_ not in processed[mod['type']][idx]['mods'][mod['tier']]['groupid']:
				processed[mod['type']][idx]['mods'][mod['tier']]['groupid'] += f" {groupid_}"

		else:
			processed[mod['type']][idx]['mods'][mod['tier']] = {
				'name': '<br>'.join(mod['mod']).replace("'", "\\'"),
				'cost': ', '.join([f'{mod["cost"][i]}<span class="{spanlookup[mod["currency"][i]]}"></span>' for i in range(len(mod['cost']))]).replace("'", "\\'"),
				'slots': ''.join([f'<span class="{spanlookup[i]}"></span>' for i in mod['bases']]),
				'slots_meta': set([f'{spanlookup[i]}' for i in mod['bases']]),
				'loc': mod['location'].replace("'", "\\'") if mod['master'] != 5 else parse_jun(mod['location'], mod['type']).replace("'", "\\'"),
				'groupid': f"{mod['master']}-{mod['groupid']}" if mod['master'] != 5 else f"{mod['master']}-{mod['groupid']}-{mod['tier']}"
			}

	# Section -> mod group -> mod -> [name, cost, slot, location, groupid]
	buf = 'mods = [\n'
	for affix in ['Prefix', 'Suffix', 'Other']:
		buf += f'\t["{affix}", [\n'
		for mod in processed[affix]:
			buf += f'\t\t["{mod["name"]}", [\n'
			for m in sorted(mod['mods']):
				buf += f"\t\t\t['{mod['mods'][m]['name']}', '{mod['mods'][m]['cost']}', '{mod['mods'][m]['slots']}', \"{' '.join(mod['mods'][m]['slots_meta'])}\", '{mod['mods'][m]['loc']}', '{mod['mods'][m]['groupid']}'],\n"
			buf += '\t\t]],\n'
		buf += '\t]],\n'
	buf += ']'
	with open('table_data.py', 'w') as f:
		f.write(buf)


def main():
	data = load_from_ggpk()
	htmlify(data)


if __name__ == '__main__':
	main()