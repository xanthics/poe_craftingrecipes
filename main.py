from browser import document as doc
from browser import html, window, bind, worker
from browser.html import TABLE, TR, TH, TD
from browser.local_storage import storage


storage_key = "poe_crafting_bench"
myWorker = worker.Worker("myworker")


# Setter storage so that we can differentiate values on this site from others at the same domain
def set_storage(key, val):
	storage["{}-{}".format(storage_key, key)] = val


# Getting for storage so that we can differentiate values on this site from others at the same domain
def get_storage(key):
	return storage["{}-{}".format(storage_key, key)]


# Check if a value exists in storage
def check_storage(key):
	return "{}-{}".format(storage_key, key) in storage


# Reset that only deletes values for this site
def reset_data(ev):
	for key in storage.keys():
		if key.startswith(storage_key):
			del storage[key]  # Generator to return all keys in storage for this site


def list_storage():
	for val in storage:
		if val.startswith(storage_key):
			yield val[len(storage_key) + 1:], storage[val]


@bind(myWorker, "message")
def onmessage(evt):
	if evt.data[0] == 'size':
		for i in range(len(evt.data[1])):
			affix = evt.data[1][i]
			section = html.DIV(Class=f"{affix}", id=f"section{affix}")
			doc["main"] <= section
			section <= html.H1(affix, id=f"{affix}") + html.BR()
			for idx in range(evt.data[2][i]):
				myWorker.send(('row', affix, i, idx))
		myWorker.send(('done',))
	elif evt.data[0] == 'button':
		affix = evt.data[1]
		mod = evt.data[2]
		name = evt.data[3]
		table = evt.data[4]
		b_generate = html.BUTTON(mod, name=name)
		doc[f"section{affix}"] <= b_generate + html.BR() + html.DIV(id=name) + TABLE(table, Class='body')
	elif evt.data[0] == 'done':
		doc["main"] <= html.DIV(id='reset')
		b_reset = html.BUTTON("Reset Data (warning not reversible)")
		b_reset.bind("click", reset_data)
		doc["reset"] <= b_reset
		# set default checkboxes to checked
		for elt in doc.get(selector='input[data-id="3-default"]'):
			elt.checked = True
		# Change style of those rows
		for elt in doc.get(selector='TR[data-id="3-default"]'):
			elt.attrs['class'] = 'checked'
		# load saved data
		for key, val in list_storage():
			binstate = bool(val)
			newstate = 'checked' if binstate else 'unchecked'
			for elt in doc.get(selector='input[data-id="{}"]'.format(key)):
				elt.checked = True
			# Change style of those rows
			for elt in doc.get(selector='TR[data-id="{}"]'.format(key)):
				elt.attrs['class'] = 'checked'

		doc["loading"].style.display = "none"

		# Bind is attached only to elements that exist when it is created
		@bind('button[name]', 'click')
		def togglemod(ev):
			name = ev.target.name
			if doc[name].style.display == "none":
				doc[name].style.display = "inline"
			else:
				doc[name].style.display = "none"

		# Function for fading rows
		@bind('input[type=checkbox]', 'click')
		def togglerow(ev):
			binstate = ev.target.checked
			newstate = 'checked' if binstate else 'unchecked'

			set_storage(ev.target.attrs['data-id'], str(binstate))
			# set default checkboxes to checked
			for elt in doc.get(selector='input[data-id="{}"]'.format(ev.target.attrs['data-id'])):
				elt.checked = binstate
			# Change style of those rows
			for elt in doc.get(selector='TR[data-id="{}"]'.format(ev.target.attrs['data-id'])):
				elt.attrs['class'] = newstate
			if doc['summary'].style.display == "block":
				printmissing()


def printmissing():
	missing = {'act': [], 'map': [], 'atzoatl': [], 'mine': [], 'prophecy': [], 'veil': {}, 'lab': []}
	# TODO: Very Slow -- fix this
	for elt in doc.get(selector='input[type="checkbox"]'):
		if not elt.checked:
			loc = elt.attrs['data-loc']
			if 'Map' in loc:
				if loc not in missing['map']:
					missing['map'].append(loc)
			elif 'Atzoatl' in loc:
				if loc not in missing['atzoatl']:
					missing['atzoatl'].append(loc)
			elif 'Azurite' in loc:
				if loc not in missing['mine']:
					missing['mine'].append(loc)
			elif 'Prophecy' in loc or 'Pale Court' in loc:
				if loc not in missing['prophecy']:
					missing['prophecy'].append(loc)
			elif 'Trial' in loc:
				if loc not in missing['lab']:
					missing['lab'].append(loc)
			elif 'veil' in loc.lower():
				slot = elt.attrs['data-slot']
				if loc not in missing['veil']:
					missing['veil'][loc] = slot.split(',')
				else:
					for s in slot.split(' '):
						if s not in missing['veil'][loc]:
							missing['veil'][loc].append(s)
			else:
				if loc not in missing['act']:
					missing['act'].append(loc)

	doc['summary'].clear()
	doc['summary'] <= html.STRONG("The following is a list of locations that have missing recipes.") + html.BR() + html.BR()
	for loc in sorted(missing):
		if missing[loc]:
			table = TABLE()
			if loc == 'act':
				table <= TH("Act Zone Name")
				for a in sorted(missing[loc]):
					table <= TR(TD(a))
			elif loc == 'map':
				table <= TH("Name")
				for a in sorted(missing[loc]):
					table <= TR(TD(a))
			elif loc == 'atzoatl':
				table <= TH("Atzoatl")
				for a in sorted(missing[loc]):
					table <= TR(TD(a.split('- ')[1]))
			elif loc == 'mine':
				table <= TH("Mines")
				for a in sorted(missing[loc]):
					table <= TR(TD(a.split(' in the')[0]))
			elif loc == 'prophecy':
				table <= TH("Prophecy")
				for a in sorted(missing[loc]):
					table <= TR(TD(a))
			elif loc == 'lab':
				table <= TH("Labyrinth")
				for a in sorted(missing[loc]):
					table <= TR(TD(a))
			elif loc == 'veil':
				table <= TH("Veiled Mod")
				table <= TH("Slot(s)")
				for a in sorted(missing[loc]):
					table <= TR(TD(a) + TD([html.SPAN(Class=x) for x in missing[loc][a]]))

			doc['summary'] <= table
	doc['summary'].style.display = "block"


def togglestate(ev):
	if doc['summary'].style.display == "none":
		printmissing()
	else:
		doc['summary'].style.display = "none"


myWorker.send(("init",))  # Hack for incremental page load part 2
doc['summary'].style.display = "none"
b_generate = html.BUTTON("Toggle Summary")
b_generate.bind("click", togglestate)
doc["togglesummary"] <= b_generate
