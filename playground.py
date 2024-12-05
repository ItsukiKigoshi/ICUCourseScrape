import helper
parsed_schedule = helper.parse_schedule("1/TH,2/TH<6/M,7/M or 6/W,7/W>")
print(f'{parsed_schedule=}')

parsed_schedule = helper.parse_schedule("5/M,(6/M,7/M)")
print(f'{parsed_schedule=}')

parsed_schedule = helper.parse_schedule("*4/TU,*4/TH")
print(f'{parsed_schedule=}')