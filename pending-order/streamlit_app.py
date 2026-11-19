# Import python packages
import streamlit as st
import os

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothie Orders! :cup_with_straw: ")
st.write(
  """Order that needs to be filled.
  """
)
#Create a database connection to Snowflake
conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()
from snowflake.snowpark.functions import col
from snowflake.snowpark.functions import when_matched

my_dataframe = session.table("smoothies.public.orders") \
    .filter(col("ORDER_FILLED") == 0) \
    .collect()
if my_dataframe:
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit')
    if submitted:
        #st.success("Someone clicked the button.", icon= '👍')
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)
        try:
            og_dataset.merge(edited_dataset
                         , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                         , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                        )
            st.success('Order(s) updated.', icon='👍')
        except:
            st.write('Something went wrong.')
else:
    st.success('There are no pending orders.', icon='👍')