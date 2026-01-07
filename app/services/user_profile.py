"""
User profile and addresses.
Provides a single source of truth for applicant info used across scripts.
"""

import os
from typing import Dict, Literal

AddressKey = Literal["clayton", "pembroke"]

_PROFILE_BASE = {
	"first_name": "Bryan",
	"last_name": "Ndum",
	"email": "bryanndum12@gmail.com",
	"phone": "984-274-7193",
	"location": "Clayton, North Carolina",  # Generic location text for single-field prompts
	"linkedin": "https://www.linkedin.com/in/bryan-ndum-99488b23a/",
	"country": "United States"
}

_ADDRESSES = {
	"clayton": {
		"address_line1": "213 Hocutt Dr",
		"city": "Clayton",
		"state": "NC",
		"zip": "27520",
		"country": "United States",
		"location": "Clayton, North Carolina"
	},
	"pembroke": {
		"address_line1": "698 Prospect Rd",
		"city": "Pembroke",
		"state": "NC",
		"zip": "28372",
		"country": "United States",
		"location": "Pembroke, North Carolina"
	}
}


def get_user_id() -> str:
	"""
	Returns the user id used for tracking.
	"""
	return os.getenv("JOBBOT_USER_ID", "bryan_test")


def get_user_info(preferred_address: AddressKey | None = None) -> Dict:
	"""
	Returns the unified user info including the selected address fields.
	- preferred_address can be 'clayton' or 'pembroke'
	- Env override: JOBBOT_ADDRESS in {'clayton','pembroke'}
	"""
	address_choice = preferred_address or os.getenv("JOBBOT_ADDRESS", "clayton").lower()
	if address_choice not in _ADDRESSES:
		address_choice = "clayton"

	address = _ADDRESSES[address_choice]
	# Merge base with address-specific fields (address fields override)
	user = {**_PROFILE_BASE, **address}
	return user


def get_all_addresses() -> Dict[str, Dict]:
	"""
	Return all known addresses.
	"""
	return _ADDRESSES.copy()


