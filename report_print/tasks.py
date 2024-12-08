# Copyright (c) 2024, CodeVenturers and contributors
# For license information, please see license.txt

def convert_to_float_literal(time_str):
	if not time_str or ":" not in time_str:
		return 0.0
	hours, minutes = time_str.split(":")
	return float(f"{hours}.{minutes}")

print(convert_to_float_literal("8:59"))
