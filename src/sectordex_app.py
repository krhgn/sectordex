import PySimpleGUI as sg
import sectordex_lib as lib
from time import sleep
import starmapdrawer

sg.theme_background_color(color='#2c2f33') # non-element bg color
sg.theme_element_background_color(color='#2c2f33') # element bg color
sg.theme_text_element_background_color(color='#2c2f33') # text elem bg color #2c2f33

sg.theme_border_width(border_width=0) # button & input field border width
sg.theme_button_color(color=('#ffffff','#4a4c51')) # button text color & button color

sg.theme_input_background_color(color='#1e2124') # input bg color 4a4c51
sg.theme_slider_color(color='#1e2124') # slider groove color 393a3d

sg.theme_input_text_color(color='#dddddd') # input box text color
sg.theme_element_text_color(color='#dddddd') # frame title text color
sg.theme_text_color(color='#dddddd') # res text, text elem and v sep color

sg.theme_slider_border_width(border_width=0) # does nothing?


# Secondary windows
def get_import_progress_window():
    layout = [
        [sg.Frame('Status', [[sg.Output(size=(40,9), echo_stdout_stderr=True)]], border_width=0)]
        #[sg.ProgressBar(10, 'h', (28, 20), k='import_progress_bar')]
    ]
    return sg.Window('Import in progress', layout, finalize=True)

def get_starmap_window(graph_bottom_left, graph_top_right):
    starmap = sg.Graph(
        canvas_size=(800, 800), 
        graph_bottom_left=graph_bottom_left, 
        graph_top_right=graph_top_right, 
        background_color='#111144',
        k='starmap_graph',
        float_values=True,
        enable_events=True,
        drag_submits=True
    )
    layout = [
        [sg.Button('Close', k='close_starmap_button')],
        [starmap]
    ]
    return sg.Window('Starmap', layout, finalize=True, element_justification='right')

def disable_planet_req_ui(main_win, disable=True):
    keys = [
        'ore_dropdown',
        'rare_ore_dropdown',
        'farmland_dropdown',
        'organics_dropdown',
        'volatiles_dropdown',
        'ruins_dropdown',
        'planet_types_listbox',
        'planet_cond_listbox',
        'hazard_slider',
        'exclusive_types_checkbox',
        'exclusive_cond_checkbox'
    ]
    # has to be done due to bug where setting disabled sets readonly to False in dropdowns
    for dropdown_key in keys[:6]:
        main_win[dropdown_key].update(disabled=disable, readonly=True)
    for key in keys[6:]:
        main_win[key].update(disabled=disable)
'''
============================================================== Import panel ==============================================================
'''
# PATH INPUT AND IMPORT BUTTON
save_import_frame_data = [
    [sg.Input(size=(133, 5), k='path_input'), sg.FileBrowse(), sg.Button('Import selected', k='import_selected_button')]
    #[sg.Input(size=(146, 5), k='import_selected_button_path', readonly=True, enable_events=True), sg.FileBrowse(button_text='Import save')]
]
save_import_frame = sg.Frame('Import save (campaign.xml file)', save_import_frame_data, border_width=0)

'''
======================================================== System requirements panel ========================================================
'''
# MINIMUM PLANET NUMBER AND MAXIMUM SYSTEM DISTANCE SLIDERS

system_req_frame_data = [
    [sg.Check('Uninhabited systems only', pad=(10, 12), disabled=True, k='uninhabited_systems_checkbox')],
    [sg.T('Desired system theme:                    ', pad=(10, 5)), sg.Combo(values=[], default_value=None, size=(40, 5), k='theme_dropdown', readonly=True, disabled=True, pad=(10, 5))],
    [sg.T('Min number of planets:                     ', pad=(10, 0)), sg.Slider(range=(0,0),default_value=0,orientation='horizontal',size=(33, 12), border_width=0, k='min_planet_num_slider', pad=(10, 0))],
    [sg.T('Max distance from map center in ly:  ', pad=(10, 0)), sg.Slider(range=(0,0),default_value=0,orientation='horizontal',size=(33, 12), resolution=5, border_width=0, k='max_dist_slider', pad=(10, 0))],
    [sg.T('', pad=(0, 0))]
    
]

system_req_frame = sg.Frame('General system requirements', system_req_frame_data, border_width=1)
'''
======================================================== Planet requirements panel ========================================================
'''
# ADDED PLANET REQUIREMENTS LIST
added_req_list = sg.Listbox(values=[], size=(74,5), pad=(9,9), enable_events=True, k='planet_req_listbox')

# PLANET TYPE LIST
planet_type_frame_data = [
    [sg.Listbox(values=[], size=(30, 8), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, k='planet_types_listbox', enable_events=True, right_click_menu=['', ['Deselect all types']])]
    #[sg.Button('Deselect all types', size=(15,1), k='deselect_all_types_button')]
]
planet_type_frame = sg.Frame('Planet Type (or)', planet_type_frame_data, border_width=0)

planet_conditions_frame_data = [
    [sg.Listbox(values=[], size=(30, 8), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, k='planet_cond_listbox', enable_events=True, right_click_menu=['', ['Deselect all conditions']])]
    #[sg.Button('Deselect all types', size=(15,1), k='deselect_all_types_button')]
]
planet_conditions_frame = sg.Frame('Planet Conditions (and)', planet_conditions_frame_data, border_width=0)

# RESOURCE DROPDOWNS
ore_level_labels = ['-', 'sparse', 'moderate', 'abundant', 'rich', 'ultrarich']
rare_ore_level_labels = ['-', 'sparse', 'moderate', 'abundant', 'rich', 'ultrarich']
farmland_level_labels = ['-', 'poor', 'adequate', 'rich', 'bountiful']
organics_level_labels = ['-', 'trace', 'common', 'abundant', 'plentiful']
volatiles_level_labels = ['-', 'trace', 'diffuse', 'abundant', 'plentiful']
ruins_level_labels = ['-', 'scattered', 'widespread', 'extensive', 'vast']
ore_level_label_id_map = dict(zip(ore_level_labels, [None] + lib.ORE_LEVELS))
rare_ore_level_label_id_map = dict(zip(rare_ore_level_labels, [None] + lib.RARE_ORE_LEVELS))
farmland_level_label_id_map = dict(zip(farmland_level_labels, [None] + lib.FARMLAND_LEVELS))
organics_level_label_id_map = dict(zip(organics_level_labels, [None] + lib.ORGANICS_LEVELS))
volatiles_level_label_id_map = dict(zip(volatiles_level_labels, [None] + lib.VOLATILES_LEVELS))
ruins_level_label_id_map = dict(zip(ruins_level_labels, [None] + lib.RUINS_LEVELS))
res_label_col = [
    [sg.T('Ore: ')],
    [sg.T('Rare ore: ')],
    [sg.T('Farmland: ')],
    [sg.T('Organics: ')],
    [sg.T('Volatiles: ')],
    [sg.T('Ruins: ')]
]
res_dropdown_col = [
    [sg.Combo(ore_level_labels, size=(21, 5), default_value=ore_level_labels[0], k='ore_dropdown', readonly=True, enable_events=True)],
    [sg.Combo(rare_ore_level_labels, size=(21, 5), default_value=rare_ore_level_labels[0], k='rare_ore_dropdown', readonly=True, enable_events=True)],
    [sg.Combo(farmland_level_labels, size=(21, 5), default_value=farmland_level_labels[0], k='farmland_dropdown', readonly=True, enable_events=True)],
    [sg.Combo(organics_level_labels, size=(21, 5), default_value=organics_level_labels[0], k='organics_dropdown', readonly=True, enable_events=True)],
    [sg.Combo(volatiles_level_labels, size=(21, 5), default_value=volatiles_level_labels[0], k='volatiles_dropdown', readonly=True, enable_events=True)],
    [sg.Combo(ruins_level_labels, size=(21, 5), default_value=ruins_level_labels[0], k='ruins_dropdown', readonly=True, enable_events=True)]
]
res_frame_data = [
                [sg.Column(res_label_col), sg.Column(res_dropdown_col)]
            ]
resources_frame = sg.Frame('Resources (minimum)', res_frame_data, border_width=0)

# HAZARD SLIDER
hazard_frame_data = [
    [sg.Slider(range=(0,25),default_value=0,orientation='horizontal',size=(28, 15), resolution=25, border_width=0, k='hazard_slider', enable_events=True)]
]
hazard_frame = sg.Frame('Maximum hazard', hazard_frame_data, border_width=0)

# MISC CHECKBOXES
misc_frame_data = [
    #[sg.Checkbox('Exclude selected planet types in search', default=False, k='exclusive_types_checkbox',tooltip='Instead of searching for the selected types, search for all types except for the ones selected.')],
    [sg.Checkbox('Exclusive planet type search mode       ', default=False, k='exclusive_types_checkbox', tooltip='Instead of looking for planets of selected type, look for planets whose type does not match any of the selected', enable_events=True)],
    [sg.Checkbox('Exclusive condition search mode', default=False, k='exclusive_cond_checkbox', tooltip='Instead of looking for planets with the selected conditions, look for planets without any of the selected conditions', enable_events=True)],
]
misc_frame = sg.Frame('Miscellaneous', misc_frame_data, border_width=0)

# REQUIREMENTS PANEL LAYOUT (left half of main window)
planet_req_col_1 = sg.Column([
    [planet_type_frame],
    [planet_conditions_frame]
])

planet_req_col_2 = sg.Column([
    [resources_frame],
    [hazard_frame],
    [misc_frame]
])
planet_req_frame_data = [
    [added_req_list],
    [sg.Button('Add requirement', pad=(9,0), size=(30,1), k='add_planet_req_button', disabled=True), sg.Button('Remove selected', pad=(9,0), size=(30,1), k='remove_planet_req_button', disabled=True)],
    [planet_req_col_1, planet_req_col_2]
]
planet_req_frame = sg.Frame('System planet requirements', planet_req_frame_data, border_width=1)


'''
======================================================== Search results panel ========================================================
'''
system_list_frame_text = 'Search results'
# FOUND SYSTEMS LIST
system_list_frame_data = [
    [sg.Listbox(values=[], size=(70,11), enable_events=True, k='systems_listbox', right_click_menu=['', ['Show on sector map']])],
    [sg.Button('Save system info', k='save_system_info_button'), sg.Button('Show on map', k='show_on_map_button')]
]
system_list_frame = sg.Frame('Search results', system_list_frame_data, element_justification='right', k='system_list_frame', border_width=1)

# SYSTEM DETAIL DESCRIPTION
system_details_frame_data = [
    [sg.Column([[sg.Text(size=(70,200), k='system_details_text', font='Courier 10', background_color='#1e2124')]], size=(492,449), scrollable=True, k='system_details_col', vertical_scroll_only=True)], #540
]
system_details_frame = sg.Frame('System details', system_details_frame_data, border_width=1)

'''
========================================================= Main layout setup =========================================================
'''
req_col = sg.Column([
    [system_req_frame],
    [planet_req_frame],
    [sg.Button('Search for systems', size=(69,2), k='search_systems_button', disabled=True, button_color=('#ffffff', '#6B3333'), pad=(3, 10))] # button_color=('white','#8B423F')
])
results_col = sg.Column([
    [system_list_frame],
    [system_details_frame]
])
layout = [
    [save_import_frame],
    [req_col, results_col]
]
main_win = sg.Window('Sectordex', layout, finalize=True)
disable_planet_req_ui(main_win, disable=True)
import_progress_win = None
starmap_win = None

'''
============================================================= Global vars ============================================================
'''
sector = lib.Sector()
drag_start_x, drag_start_y = 0, 0
drag_offset_x, drag_offset_y = 0, 0
is_dragging = False

default_hazard = 0
'''
=========================================================== GUI event loop ===========================================================
'''

def update_ui_params_from_selected_planet_req(main_win):
    if values['planet_req_listbox']:
        selected = values['planet_req_listbox'][0]
        # type
        main_win['planet_types_listbox'].set_value(selected.desired_types)
        if selected_type_indexes := main_win['planet_types_listbox'].get_indexes():
            main_win['planet_types_listbox'].update(scroll_to_index=selected_type_indexes[0])
        else:
            main_win['planet_types_listbox'].update(scroll_to_index=0)
        # cond
        main_win['planet_cond_listbox'].set_value(selected.desired_conditions)
        if selected_cond_indexes := main_win['planet_cond_listbox'].get_indexes():
            main_win['planet_cond_listbox'].update(scroll_to_index=selected_cond_indexes[0])
        else:
            main_win['planet_cond_listbox'].update(scroll_to_index=0)


        # res
        main_win['ore_dropdown'].update(set_to_index=0)
        main_win['rare_ore_dropdown'].update(set_to_index=0)
        main_win['farmland_dropdown'].update(set_to_index=0)
        main_win['organics_dropdown'].update(set_to_index=0)
        main_win['volatiles_dropdown'].update(set_to_index=0)
        main_win['ruins_dropdown'].update(set_to_index=0)
        for resource in selected.desired_resources:
            if resource in lib.ORE_LEVELS:
                main_win['ore_dropdown'].update(set_to_index=lib.ORE_LEVELS.index(resource)+1)
            elif resource in lib.RARE_ORE_LEVELS:
                main_win['rare_ore_dropdown'].update(set_to_index=lib.RARE_ORE_LEVELS.index(resource)+1)
            elif resource in lib.FARMLAND_LEVELS:
                main_win['farmland_dropdown'].update(set_to_index=lib.FARMLAND_LEVELS.index(resource)+1)
            elif resource in lib.ORGANICS_LEVELS:
                main_win['organics_dropdown'].update(set_to_index=lib.ORGANICS_LEVELS.index(resource)+1)
            elif resource in lib.VOLATILES_LEVELS:
                main_win['volatiles_dropdown'].update(set_to_index=lib.VOLATILES_LEVELS.index(resource)+1)
            elif resource in lib.RUINS_LEVELS:
                main_win['ruins_dropdown'].update(set_to_index=lib.RUINS_LEVELS.index(resource)+1)
        main_win['hazard_slider'].update(value=selected.desired_hazard*100)
        main_win['exclusive_types_checkbox'].update(value=selected.exclusive_type_mode)
        main_win['exclusive_cond_checkbox'].update(value=selected.exclusive_cond_mode)



def update_req_list_from_ui(main_win, values):
    req_list = main_win['planet_req_listbox'].get_list_values()
    if values['planet_req_listbox']:
        selected_req = values['planet_req_listbox'][0]
        selected_req_index = req_list.index(selected_req)
        # get types from ui
        new_types = main_win['planet_types_listbox'].get()
        # get conditions from ui
        new_conditions = main_win['planet_cond_listbox'].get()
        # get resource reqs from ui
        new_resources = []
        if (ore_level := ore_level_label_id_map[main_win['ore_dropdown'].get()]) is not None:
            new_resources.append(ore_level)
        if (rare_ore_level := rare_ore_level_label_id_map[main_win['rare_ore_dropdown'].get()]) is not None:
            new_resources.append(rare_ore_level)
        if (farmland_level := farmland_level_label_id_map[main_win['farmland_dropdown'].get()]) is not None:
            new_resources.append(farmland_level)
        if (organics_level := organics_level_label_id_map[main_win['organics_dropdown'].get()]) is not None:
            new_resources.append(organics_level)
        if (volatiles_level := volatiles_level_label_id_map[main_win['volatiles_dropdown'].get()]) is not None:
            new_resources.append(volatiles_level)
        if (ruins_level := ruins_level_label_id_map[main_win['ruins_dropdown'].get()]) is not None:
            new_resources.append(ruins_level)
        # get hazard from ui
        new_hazard = values['hazard_slider']/100
        # create planet req object
        new_planet_req = lib.PlanetReq(
            desired_types=new_types, 
            desired_conditions=new_conditions,
            desired_resources=new_resources, 
            desired_hazard=new_hazard,
            exclusive_type_mode=values['exclusive_types_checkbox'],
            exclusive_cond_mode=values['exclusive_cond_checkbox']
        )
        updated_req_list = req_list[:selected_req_index] + [new_planet_req] + req_list[selected_req_index+1:]
        main_win['planet_req_listbox'].update(values=updated_req_list, set_to_index=updated_req_list.index(new_planet_req))

req_update_keys = [
    'planet_types_listbox',
    'ore_dropdown',
    'rare_ore_dropdown',
    'farmland_dropdown',
    'organics_dropdown',
    'volatiles_dropdown',
    'ruins_dropdown',
    'hazard_slider',
    'planet_cond_listbox',
    'exclusive_types_checkbox',
    'exclusive_cond_checkbox'
]

def reset_planet_req_ui(main_win):
    # reset planet req panel slider/dropdown/selection values to default
    main_win['planet_types_listbox'].SetValue([])
    main_win['planet_cond_listbox'].SetValue([])
    main_win['hazard_slider'].update(value=default_hazard)
    main_win['ore_dropdown'].update(set_to_index=0)
    main_win['rare_ore_dropdown'].update(set_to_index=0)
    main_win['farmland_dropdown'].update(set_to_index=0)
    main_win['organics_dropdown'].update(set_to_index=0)
    main_win['volatiles_dropdown'].update(set_to_index=0)
    main_win['ruins_dropdown'].update(set_to_index=0)
    main_win['exclusive_types_checkbox'].update(value=False)
    main_win['exclusive_cond_checkbox'].update(value=False)
    
def append_pad_to_length(string, length):
    string = str(string)
    if length > len(string):
        return string + ' '*(length-len(string))
    else:
        raise Exception(f'Invalid padding length for string: {string}')

def get_detail_string(sys):
    detail_string = f'{sys.name}\n'
    if sys.is_inhabited:
        detail_string += 'System is inhabited\n'
    detail_string += f'System coordinates: ({sys.loc[0]:0.1f}ly, {sys.loc[1]:0.1f}ly)\n' 
    detail_string += f'Distance from center: {sys.dist:0.1f}ly\n'
    detail_string += f'Jump points: {sys.num_jump_points}\n'
    if sys.stars:
        detail_string += f'Stars: {", ".join([star.type.name for star in sys.stars])}\n'

    if sys.themes:
        first_iter = True
        detail_string += f'\nSystem themes:\n'
        for theme in sys.themes:
            if first_iter:
                first_iter = False
                theme_string = f'└───{theme}\n'
            else:
                theme_string = f'├───{theme}\n' + theme_string
    detail_string += theme_string

    if sys.stations:
        first_iter = True
        detail_string += f'\nStation markets:\n'
        for station in sys.stations:
            if first_iter:
                first_iter = False
                station_string = f'└───{station}\n'
            else:
                station_string = f'├───{station}\n' + station_string
        detail_string += station_string

    if sys.stable_locs:
        first_iter = True
        detail_string += f'\nStable locations:\n'
        for stable_loc in sys.stable_locs:
            if first_iter:
                first_iter = False
                stable_loc_string = f'└───{stable_loc}\n'
            else:
                stable_loc_string = f'├───{stable_loc}\n' + stable_loc_string
        detail_string += stable_loc_string
        
    if sys.salvageables_dict:
        first_iter = True
        detail_string += f'\nSalvageables:\n'
        for k, v in sys.salvageables_dict.items():
            if first_iter:
                first_iter = False
                salvageables_string = f'└───{k}: {v}\n'
            else:
                salvageables_string = f'├───{k}: {v}\n' + salvageables_string
        detail_string += salvageables_string

    if sys.planets:
        detail_string += f'\nContains {len(sys.planets)} planets:\n'
    # whitespace padding is the longest condition string length + 5
    padding = len(sorted(sector.all_conditions, key=lambda cond: len(cond.name), reverse=True)[0].name) + 5
    for i, planet in enumerate(sorted(sys.planets, key=lambda p: p.hazard)):
        detail_string += f'\n{i+1}. {planet}:\n'
        if planet.resources:
            if planet.hazard_conditions:
                detail_string += '├───Resources:\n'
            else:
                detail_string += '└───Resources:\n'
            first_iter = True
            res_string = ''
            for res in reversed(planet.resources):
                res_name = res.name
                res_val_str = str(res.resource_level)
                if float(res_val_str) > 0:
                    res_val_str = '+' + res_val_str
                elif float(res_val_str) == 0:
                    res_val_str = ' ' + res_val_str
                if first_iter:
                    res_string = '   ' + f'└───{append_pad_to_length(res_name, padding)} {res_val_str}\n'
                    first_iter = False
                else:
                    res_string = '   ' + f'├───{append_pad_to_length(res_name, padding)} {res_val_str}\n' + res_string
                if planet.hazard_conditions:
                    res_string = '│' + res_string
                else:
                    res_string = ' ' + res_string
            detail_string += res_string

        if planet.hazard_conditions:
            if planet.other_conditions:
                detail_string += '├───Hazard conditions:\n'
            else:
                detail_string += '└───Hazard conditions:\n'
            first_iter = True
            haz_string = ''
            for haz_cond in reversed(planet.hazard_conditions):
                haz_cond_name = haz_cond.name
                haz_val = int(100*haz_cond.hazard)
                haz_val_str = str(haz_val)
                if haz_val > 0:
                    haz_val_str = '+' + haz_val_str
                haz_val_str += '%'
                if first_iter:
                    haz_string = '   ' + f'└───{append_pad_to_length(haz_cond_name, padding)} {haz_val_str}\n'
                    first_iter = False
                else:
                    haz_string = '   ' + f'├───{append_pad_to_length(haz_cond_name, padding)} {haz_val_str}\n' + haz_string
                if planet.other_conditions:
                    haz_string = '│' + haz_string
                else:
                    haz_string = ' ' + haz_string
            detail_string += haz_string

        if planet.other_conditions:
            detail_string += '└───Other conditions:\n'
            first_iter = True
            other_string = ''
            for other_cond in reversed(planet.other_conditions):
                other_cond_name = other_cond.name
                if first_iter:
                    other_string = '    ' + f'└───{append_pad_to_length(other_cond_name, padding)}\n'
                    first_iter = False
                else:
                    other_string = '    ' + f'├───{append_pad_to_length(other_cond_name, padding)}\n' + other_string
            detail_string += other_string

    
    return detail_string

while True:
    win, event, values = sg.read_all_windows()
    if event == sg.WIN_CLOSED:
        if win is import_progress_win:
            pass
        elif win is not main_win:
            win.close()
        else:
            break

    elif event in req_update_keys:
        update_req_list_from_ui(main_win, values)

    # show on map handler
    elif event == 'show_on_map_button' or event == 'Show on sector map':
        if values['systems_listbox']:
            selected_system = values['systems_listbox'][0]
            if starmap_win is not None:
                starmap_win.close()
            canvas_lower_left, canvas_top_right, canvas_size, canvas_center = starmapdrawer.get_viewport_params(selected_system)
            starmap_win = get_starmap_window(canvas_lower_left, canvas_top_right)
            starmapdrawer.draw_polar_axes(starmap_win['starmap_graph'], radius=sector.max_system_dist, canvas_size=canvas_size)
            starmapdrawer.draw_stars(starmap_win['starmap_graph'], sector.systems, canvas_size)
            starmapdrawer.draw_labels(starmap_win['starmap_graph'], sector.systems, selected_system, canvas_size)

    elif event == 'close_starmap_button':
        starmap_win.close()

    # importing save file handler
    elif event == 'import_selected_button':
        path = main_win['path_input'].get()
        import_progress_win = get_import_progress_window()
        try:
            sector.load_from_xml(path)
            # enabling so that the list gets visually updated, then disabling after
            main_win['planet_types_listbox'].update(values=sorted(list(sector.planet_types)), disabled=False)
            main_win['planet_types_listbox'].update(disabled=True)
            main_win['planet_cond_listbox'].update(values=sorted(list(sector.all_conditions)), disabled=False)
            main_win['planet_cond_listbox'].update(disabled=True)
            main_win['max_dist_slider'].update(range=(0, sector.max_system_dist))
            main_win['max_dist_slider'].update(value=sector.max_system_dist)
            main_win['min_planet_num_slider'].update(range=(0, sector.max_system_planet_num))
            main_win['min_planet_num_slider'].update(value=0)
            main_win['theme_dropdown'].update(values=[None] + sorted(list(sector.all_themes)), set_to_index=0, disabled=False, readonly=True)
            main_win['uninhabited_systems_checkbox'].update(disabled=False)

            main_win['hazard_slider'].update(range=[100*hazard for hazard in sector.get_hazard_range()])
            default_hazard = 100*sector.get_hazard_range()[1]
            main_win['hazard_slider'].update(value=default_hazard)

            print('Import complete')
            sleep(0.5)
            main_win['add_planet_req_button'].update(disabled=False)
            main_win['remove_planet_req_button'].update(disabled=False)
            main_win['search_systems_button'].update(disabled=False)
        except OSError:
            sg.popup('Invalid path')
        import_progress_win.close()
    
    elif event == 'planet_req_listbox':
        req_list = main_win['planet_req_listbox'].get_list_values()
        if values['planet_req_listbox']:
            update_ui_params_from_selected_planet_req(main_win)
            disable_planet_req_ui(main_win, disable=False)

            if selected_type_indexes := main_win['planet_types_listbox'].get_indexes():
                main_win['planet_types_listbox'].update(scroll_to_index=selected_type_indexes[0])
            else:
                main_win['planet_types_listbox'].update(scroll_to_index=0)
            if selected_cond_indexes := main_win['planet_cond_listbox'].get_indexes():
                main_win['planet_cond_listbox'].update(scroll_to_index=selected_cond_indexes[0])
            else:
                main_win['planet_cond_listbox'].update(scroll_to_index=0)
    

    elif event == 'remove_planet_req_button':
        curr_reqs = main_win['planet_req_listbox'].get_list_values()
        try:
            selected_val = values['planet_req_listbox'][0]
            curr_reqs.remove(selected_val)
            main_win['planet_req_listbox'].update(values=curr_reqs)
            reset_planet_req_ui(main_win)
            disable_planet_req_ui(main_win, disable=True)
        except IndexError:
            pass

    elif event == 'Deselect all types':
        main_win['planet_types_listbox'].SetValue([])
        update_req_list_from_ui(main_win, values)

    elif event == 'Deselect all conditions':
        main_win['planet_cond_listbox'].SetValue([])
        update_req_list_from_ui(main_win, values)

    # pressing add new planet req handler
    elif event == 'add_planet_req_button':
        new_req_list = main_win['planet_req_listbox'].get_list_values() + [lib.PlanetReq(desired_hazard=default_hazard/100)]
        new_req_index = len(new_req_list)-1
        main_win['planet_req_listbox'].update(values=new_req_list, set_to_index=new_req_index, scroll_to_index=new_req_index)
        reset_planet_req_ui(main_win)
        disable_planet_req_ui(main_win, disable=False)
        main_win['planet_types_listbox'].update(scroll_to_index=0)
        main_win['planet_cond_listbox'].update(scroll_to_index=0)

    # pressing search button handler
    elif event == 'search_systems_button':
        system_requirement = lib.StarSystemReq(
            max_distance=values['max_dist_slider'], 
            min_planet_num=values['min_planet_num_slider'], 
            planet_reqs=main_win['planet_req_listbox'].get_list_values(),
            desired_theme=values['theme_dropdown'],
            must_be_uninhabited=values['uninhabited_systems_checkbox']
        )
        matching_systems = sector.get_matching_systems(system_requirement)
        main_win['system_list_frame'].update(value=f'{system_list_frame_text} ({len(matching_systems)})')
        main_win['systems_listbox'].update(values=sorted(matching_systems, key=lambda system: system.dist))
        main_win['system_details_text'].update(value='')

    # selecting a system in the results handler
    elif event == 'systems_listbox':
        if values['systems_listbox']:
            sys = values['systems_listbox'][0]
            detail_string = get_detail_string(sys)
        else:
            detail_string = ''
        details_height = len(detail_string.split('\n'))
        #print(main_win['system_details_text'].get_size(), details_height*3)
        #main_win['system_details_text'].set_size(size=(None, details_height*3))
        #print(main_win['system_details_text'].get_size())
        main_win['system_details_text'].update(value=detail_string)  
        main_win['system_details_col'].Widget.canvas.yview_moveto(0.0)
        

    # mouse panning in the starmap handlers
    elif event == 'starmap_graph+UP':
        drag_offset_x, drag_offset_y = 0, 0
        is_dragging = False
        
    elif event == 'starmap_graph':
        if not is_dragging:
            drag_start_x, drag_start_y = values['starmap_graph']
            is_dragging = True
        else:
            starmap_win['starmap_graph'].move(-drag_offset_x, -drag_offset_y)
            drag_curr_x, drag_curr_y = values['starmap_graph']
            drag_offset_x = drag_curr_x - drag_start_x
            drag_offset_y = drag_curr_y - drag_start_y
            starmap_win['starmap_graph'].move(drag_offset_x, drag_offset_y)
    
    elif event == 'save_system_info_button':
        
        if values['systems_listbox']:
            sys = values['systems_listbox'][0]
            filename = f'{sector.name} {sys.name}.txt'
            detail_string = get_detail_string(sys)
            with open(filename, 'w', encoding="utf-8") as output:
                output.write(f'{sys.name}\n{sector.seed}\n\n' + detail_string + '\n' + 50*'=' + '\n')
            sg.popup(f'Saved {sys.name} from {sector.name} to file')
    else:
        print(event)

main_win.close()


'''
Todo:

Mutually exclusive planet reqs checkbox

Stable locs/Comm relays/Nav buoys/Sensor arrays slider

Only uninhabited systems checkbox

Check missing planets like in galatia, then look for them in the xml and find out why they ain't gettin picked up by the script

Sorting options for search results/system details?

'''