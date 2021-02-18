import PySimpleGUI as sg
from math import ceil
from numpy.linalg import norm
from random import sample

# star drawing sizes
SIZE_SUPERGIANT = 0.4
SIZE_GIANT = 0.3
SIZE_NORMAL = 0.2
SIZE_DWARF = 0.1

# color strings
STAR_BROWN = 'maroon'
STAR_RED = '#bb0000'
STAR_ORANGE = 'darkorange'
STAR_YELLOW = 'gold'
STAR_WHITE = 'whitesmoke'
STAR_BLUE = 'aqua'

# radius, fill color, line color, line width
STAR_DRAW_PARAMS = {
    'star_red_supergiant':[SIZE_SUPERGIANT, STAR_RED],
    'star_blue_supergiant':[SIZE_SUPERGIANT, STAR_BLUE], 
    'star_red_giant':[SIZE_GIANT, STAR_RED], 
    'US_star_red_giant':[SIZE_GIANT, STAR_RED],
    'star_blue_giant':[SIZE_GIANT, STAR_BLUE], 
    'US_star_blue_giant':[SIZE_GIANT, STAR_BLUE],      
    'star_orange_giant':[SIZE_GIANT, STAR_ORANGE], 
    
    'star_yellow':[SIZE_NORMAL, STAR_YELLOW], 
    'US_star_yellow':[SIZE_NORMAL, STAR_YELLOW], 
    'star_orange':[SIZE_NORMAL, STAR_ORANGE], 
    'star_neutron':[SIZE_DWARF, 'lightcyan'], 
    'star_white':[SIZE_DWARF, STAR_WHITE], 
    
    'US_star_white':[SIZE_DWARF, STAR_WHITE], 
    'star_red_dwarf':[SIZE_DWARF, STAR_RED],
    'star_browndwarf':[SIZE_DWARF, STAR_BROWN], 
    'US_star_browndwarf':[SIZE_DWARF, STAR_BROWN], 
    'black_hole':[SIZE_NORMAL, 'black', 'white', 1],
    'istl_sigmaworld':[SIZE_NORMAL, 'limegreen'],
}

def round_up_to_multiple_of_n(num, n):
    return ceil(num/n)*n

def get_viewport_params(selected_system):
    canvas_padding = 10
    canvas_size = max(abs(selected_system.loc[0]), abs(selected_system.loc[1])) + 2*canvas_padding
    canvas_center = [coord/2 for coord in selected_system.loc]
    canvas_lower_left = (canvas_center[0] - canvas_size/2, canvas_center[1] - canvas_size/2)
    canvas_top_right = (canvas_center[0] + canvas_size/2, canvas_center[1] + canvas_size/2)
    return canvas_lower_left, canvas_top_right, canvas_size, canvas_center

def draw_polar_axes(starmap_graph, radius, canvas_size):
    tick_interval = 5
    radius = round_up_to_multiple_of_n(radius, tick_interval)
    color = '#2222aa'
    line_width = 30/canvas_size
    font = f'Helvetica {max(int(100/canvas_size), 8)}'
    padding = 0.2

    starmap_graph.draw_line((0, radius), (0, -radius), color, line_width)
    starmap_graph.draw_line((radius, 0), (-radius, 0), color, line_width)
    for dist in range(tick_interval, radius, tick_interval):
        starmap_graph.draw_circle((0,0), dist, None, color, line_width)
        starmap_graph.draw_text(f'{dist}LY', (dist+padding, 2*padding), color, font, text_location=sg.TEXT_LOCATION_LEFT)
        starmap_graph.draw_text(f'{dist}LY', (-dist-padding, 2*padding), color, font, text_location=sg.TEXT_LOCATION_RIGHT)
        starmap_graph.draw_text(f'{dist}LY', (padding, dist+2*padding), color, font, text_location=sg.TEXT_LOCATION_LEFT)
        starmap_graph.draw_text(f'{dist}LY', (padding, -dist-2*padding), color, font, text_location=sg.TEXT_LOCATION_LEFT)
            
def draw_stars(starmap_graph, systems, canvas_size):
    for system in systems:
        x, y = system.loc
        # if inhabited: draw text
        if system.stars:
            if (star_type_id := system.stars[0].type.id) in STAR_DRAW_PARAMS:
                starmap_graph.draw_circle(*([(x,y)] + STAR_DRAW_PARAMS[star_type_id]))
            else:
                print('key error', star.id)
                starmap_graph.draw_circle((x,y), SIZE_NORMAL, 'white')
                starmap_graph.draw_text('?', (x, y), 'black', 'Helvetica 6 bold')

        elif system.name.endswith('Nebula'):
            nebula_thickness = 150/canvas_size
            starmap_graph.draw_circle((x,y), 0.4, None, 'indigo', nebula_thickness)

        else:
            # default star
            starmap_graph.draw_circle(*([(x,y)] + STAR_DRAW_PARAMS['star_yellow']))

def draw_labels(starmap_graph, systems, selected_system, canvas_size):
    padding = canvas_size/50
    font = f'Helvetica {max(int(120/canvas_size), 11)}'
    color = 'white'
    secondary_font = f'Helvetica {max(int(100/canvas_size), 8)}'
    secondary_color = '#3344ff'
    neighborhood_radius = 5
    neighboring_systems = []
    for system in systems:
        if system != selected_system:
            x, y = system.loc
            distance_to_selected = norm((system.loc[0] - selected_system.loc[0], system.loc[1] - selected_system.loc[1]))
            if system.is_claimed:
                starmap_graph.draw_line((x, y), [coord+padding for coord in (x, y)], secondary_color, 1)
                starmap_graph.draw_text(system.name.removesuffix(' Star System'), [coord+padding for coord in (x, y)], secondary_color, secondary_font + ' italic', text_location=sg.TEXT_LOCATION_LEFT)
            elif distance_to_selected < neighborhood_radius:
                neighboring_systems.append(system)
    for neighbor in sample(neighboring_systems, min(len(neighboring_systems), 4)):
        x, y = neighbor.loc
        starmap_graph.draw_line((x, y), [coord+padding for coord in (x, y)], secondary_color, 1)
        starmap_graph.draw_text(neighbor.name.removesuffix(' Star System'), [coord+padding for coord in (x, y)], secondary_color, secondary_font + ' italic', text_location=sg.TEXT_LOCATION_LEFT)
    starmap_graph.draw_line(selected_system.loc, [coord+padding for coord in selected_system.loc], color, 1)
    starmap_graph.draw_text(selected_system.name, [coord+padding for coord in selected_system.loc], color, font, text_location=sg.TEXT_LOCATION_LEFT)
