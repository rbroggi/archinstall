from __future__ import annotations

import json
import os
import gettext

from pathlib import Path
from typing import List, Dict


class Languages:
	def __init__(self):
		self._mappings = self._get_language_mappings()

	def _get_language_mappings(self) -> List[Dict[str, str]]:
		locales_dir = Translation.get_locales_dir()
		languages = Path.joinpath(locales_dir, 'languages.json')

		with open(languages, 'r') as fp:
			return json.load(fp)

	def get_language(self, abbr: str) -> str:
		for entry in self._mappings:
			if entry['abbr'] == abbr:
				return entry['lang']

		raise ValueError(f'No language with abbrevation "{abbr}" found')


class DeferredTranslation:
	def __init__(self, message):
		self.message = message

	def __len__(self) -> int:
		return len(self.message)

	def __str__(self) -> str:
		translate = _
		if translate is DeferredTranslation:
			return self.message
		return translate(self.message)

	@classmethod
	def install(cls):
		import builtins
		builtins._ = cls


class Translation:
	def __init__(self, locales_dir):
		DeferredTranslation.install()

		self._languages = {}

		for name in self.get_all_names():
			self._languages[name] = gettext.translation('base', localedir=locales_dir, languages=[name])

	def activate(self, name):
		if language := self._languages.get(name, None):
			language.install()
		else:
			raise ValueError(f'Language not supported: {name}')

	@classmethod
	def load_nationalization(cls) -> Translation:
		locales_dir = cls.get_locales_dir()
		return Translation(locales_dir)

	@classmethod
	def get_locales_dir(cls) -> Path:
		cur_path = Path(__file__).parent.parent
		locales_dir = Path.joinpath(cur_path, 'locales')
		return locales_dir

	@classmethod
	def get_all_names(cls) -> List[str]:
		locales_dir = cls.get_locales_dir()
		filenames = os.listdir(locales_dir)
		def_languages = filter(lambda x: len(x) == 2, filenames)

		languages = Languages()
		return [languages.get_language(lang) for lang in def_languages]