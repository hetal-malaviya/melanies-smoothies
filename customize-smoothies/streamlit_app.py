# Import python packages
import streamlit as st
import os
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :cup_with_straw: ")
st.write(
  """Choose the fruits in your custom Smoothie!
  """
)

from snowflake.snowpark.functions import col
name_on_order = st.text_input('Name on Smoothie')
st.write('The name in your smoothie will be', name_on_order)
#Create a database connection to Snowflake
conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, width='Stretch')
#st.stop()

#convert the snowpark Dataframe to a Pandas Dataframe so we can use the LOC function 
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect('Choose upto 5 ingridients:', my_dataframe,max_selections=5)
if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+fruit_chosen) 
        sf_df = st.dataframe(data=smoothiefroot_response.json(),width='stretch') 
        #st.text(smoothiefroot_response.json())
    #st.write(ingredients_string)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                    values ('""" + ingredients_string + """' ,'"""+name_on_order+"""')"""
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered! '+name_on_order, icon="✅")
    #st.write(my_insert_stmt)
    st.stop()
