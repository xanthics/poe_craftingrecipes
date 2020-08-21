from browser import bind, self
from table_data import mods


@bind(self, "message")
def message(evt):
	# "init"
	if evt.data[0] == 'init':
		affixes = []
		lens = []
		for affix, data in mods:
			affixes.append(affix)
			lens.append(len(data))
		self.send(('size', affixes, lens))
	# 'row', affix, i, idx
	elif evt.data[0] == 'row':
		affix = evt.data[1]
		c = evt.data[3]
		name = f"{affix}{c}"
		mod = mods[evt.data[2]][1][evt.data[3]][0]
		# Generate collapsable table
		ret_str = []
		for modname, cost, slots, slot_meta, loc, _id in mods[evt.data[2]][1][evt.data[3]][1]:
			ret_str.append(f'<tr class="unchecked" data-id="{_id}">')
			ret_str.append(f'<td class="fixedcheck"><input type="checkbox" data-id="{_id}" data-loc="{loc}", data-slot="{slot_meta}"></td>')
			ret_str.append(f'<td>{modname}</td>')
			ret_str.append(f'<td class="fixedcost">{cost}</td>')
			ret_str.append(f'<td class="fixedclass">{slots}</td>')
			ret_str.append(f'<td class="fixedloc">{loc}</td>')
			ret_str.append('</tr>')
		self.send(('button', affix, mod, name, '\n'.join(ret_str)))
	elif evt.data[0] == 'done':
		self.send(('done',))




