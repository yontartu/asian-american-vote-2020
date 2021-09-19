import streamlit as st
import pandas as pd
import os
import bokeh
from bokeh.plotting import figure, output_notebook, show
from bokeh.models import LinearColorMapper, NumeralTickFormatter
from bokeh.models.tools import HoverTool


def main():
	"""
	Structure and page logic for main Streamlit app.
	"""
	st.title('2020 Asian American Vote Choice Trends')

	# define subgroup input dict
	input_subg_dict = {
		'Asian - Total': 'pct_asian_total',
		'Asian - Other (specified)': 'pct_asian_other_specified',
		'Asian - Other (not specified)': 'pct_asian_other_not_specified',
		'Asian - Two or more races': 'pct_asian_two_more',
		'Bangladeshi': 'pct_asian_bangladeshi', 
		'Bhutanese': 'pct_asian_bhutanese',
		'Burmese': 'pct_asian_burmese', 
		'Cambodian': 'pct_asian_cambodian',
		'Chinese': 'pct_asian_chinese',
		'Filipino': 'pct_asian_filipino',
		'Hmong': 'pct_asian_hmong', 
		'Indian': 'pct_asian_indian',
		'Indonesian': 'pct_asian_indonesian',
		'Japanese': 'pct_asian_japanese',
		'Korean': 'pct_asian_korean',
		'Laotian': 'pct_asian_laotian',
		'Malaysian': 'pct_asian_malaysian',
		'Mongolian': 'pct_asian_mongolian',
		'Nepalese': 'pct_asian_nepalese',
		'Okinawan': 'pct_asian_okinawan',
		'Pakistani': 'pct_asian_pakistani', 
		'Sri Lankan': 'pct_asian_sri_lankan', 
		'Taiwanese': 'pct_asian_taiwanese',
		'Thai': 'pct_asian_thai', 
		'Vietnamese': 'pct_asian_vietnamese'
	}

	# read in asian vote 2020
	aa_pres_2020_df = pd.read_csv('data/aa_pres_2020_df.csv')
	aa_sen_2020_df = pd.read_csv('data/aa_sen_2020_df.csv')
	state_list = list(aa_pres_2020_df.state.unique())

	# build sidebar
	with st.sidebar:
		# st.info("🔎 Select the **Asian subgroup** and **state** you want to explore!")
		st.write("## Asian Subgroup")
		subg_input = st.selectbox("Which Asian subgroup do you want to explore?", list(input_subg_dict.keys()))
		new_col = input_subg_dict[subg_input] + '_display'

		st.write("## State")
		state = st.selectbox("Which state do you want displayed?", ['US overall'] + state_list)

		if state == 'US overall':
			aa_pres = aa_pres_2020_df[['state_name', 'state', 'county_name', 'dem_twoway_pres', 'dem_twoway_pres_display', 
									   'pop_total', input_subg_dict[subg_input]]]	
			aa_sen = aa_sen_2020_df[['state_name', 'state', 'county_name', 'dem_twoway_sen', 'dem_twoway_sen_display',
									   'pop_total', input_subg_dict[subg_input]]]			
			aa_pres[new_col] = aa_pres[input_subg_dict[subg_input]].apply(lambda x: str(round(x*100, 1))+'%')
			aa_sen[new_col] = aa_sen[input_subg_dict[subg_input]].apply(lambda x: str(round(x*100, 1))+'%')
		else:
			aa_pres = aa_pres_2020_df[aa_pres_2020_df.state == state][['state_name', 'state', 'county_name', 'dem_twoway_pres', 'dem_twoway_pres_display', 
									   'pop_total', input_subg_dict[subg_input]]]	
			aa_sen = aa_sen_2020_df[aa_sen_2020_df.state == state][['state_name', 'state', 'county_name', 'dem_twoway_sen', 'dem_twoway_sen_display',
									   'pop_total', input_subg_dict[subg_input]]]			
			aa_pres[new_col] = aa_pres[input_subg_dict[subg_input]].apply(lambda x: str(round(x*100, 1))+'%')
			aa_sen[new_col] = aa_sen[input_subg_dict[subg_input]].apply(lambda x: str(round(x*100, 1))+'%')

		st.write("## Electoral Race")
		electoral_race = st.selectbox('', ['President', 'Senate'])
		if electoral_race == 'President':
			data = aa_pres
			corr_r = data[input_subg_dict[subg_input]].corr(data.dem_twoway_pres)
			yvar = 'dem_twoway_pres'
			yvar_display = 'dem_twoway_pres_display'
			xvar_display = str(input_subg_dict[subg_input]) + '_display'
		elif electoral_race == 'Senate':
			data = aa_sen
			corr_r = data[input_subg_dict[subg_input]].corr(data.dem_twoway_sen)
			yvar = 'dem_twoway_sen'
			yvar_display = 'dem_twoway_sen_display'
			xvar_display = str(input_subg_dict[subg_input]) + '_display'

		st.write("## Optional: Counties")
		counties = st.multiselect("Which set of counties do you want to filter to?", list(aa_pres.county_name.unique()))	
		if st.button('Filter to selected counties'):
			data = data[data.county_name.isin(counties)]

	# build bokeh chart
	st.write(f'### {subg_input} county-level vote in {state} for {electoral_race}')
	st.write(f'Correlation = {round(corr_r, 3)}')

	color_mapper = LinearColorMapper(palette=tuple(reversed(bokeh.palettes.RdBu11)), 
									 low=0,
									 high=1)
	p = figure(title='',
			   x_axis_label=f'% of county {subg_input}',
			   y_axis_label=f'Dem. twoway voteshare for {electoral_race}',
			   width=800,
			   height=500)
	r = p.scatter(input_subg_dict[subg_input], yvar, source=data,
				   line_color="black", 
				   color={'field': yvar, 'transform': color_mapper},  
				   fill_alpha=0.4, 
				   size=10
				  )
	p.add_tools(HoverTool(
		tooltips=[
			('County', '@county_name'),
			('State', '@state'),
			(f'% {subg_input}', f'@{xvar_display}'),
			(f'Dem. Twoway Voteshare for {electoral_race}', f'@{yvar_display}')
		]))

	p.legend.click_policy="hide"
	p.legend.location = "bottom_right"
	p.xaxis.formatter = NumeralTickFormatter(format='0%')
	p.yaxis.formatter = NumeralTickFormatter(format='0%')
	st.bokeh_chart(p)

	# footnote
	st.write('Source: American Community Survey 2019, [Amlani & Algara (2021)](https://www.sciencedirect.com/science/article/abs/pii/S0261379421001050?dgcid=author#b5)')


if __name__ == "__main__":
	main()