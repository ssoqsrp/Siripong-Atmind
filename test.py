import streamlit as st
import pandas as pd
import plotly.express as px
import calendar as cl
import datetime as dt

from plotly.subplots import make_subplots
import plotly.graph_objects as go

df = pd.read_csv("test_data.csv")

# Convert 'Serve Time' and 'Order Time' columns to datetime
df['Serve Time'] = pd.to_datetime(df['Serve Time'])
df['Order Time'] = pd.to_datetime(df['Order Time'])

# Calculate the time taken to serve
df['Time Taken to Serve'] = df['Serve Time'] - df['Order Time']

# Convert "Date" column to datetime
df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

_month = pd.to_datetime(df['Date']).dt.month
month = _month.apply(lambda x: cl.month_name[x])

df['month'] =month

month_order = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
df['Month_Number'] = df['month'].map(month_order)

# Aggregate total sales for each category in each month
agg_price = df.groupby(['Month_Number', 'Category'], as_index=False)['Price'].sum()

# Create Quantity column
df['Quantity'] = 1






df.head()

df.info()

st.set_page_config(layout='wide')
st.title('Retail Analytics')

# Set layout to start from the left
st.markdown(
    """
    <style>
    body {
        display: flex;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Create two columns layout
col1, col2 = st.columns(2)

# Line Chart for Quantity by Category and Month
with col1:
    quantity_by_category_month = df.groupby(['Category', 'Month_Number']).agg({'Menu': 'count'}).reset_index()
    quantity_by_category_month = quantity_by_category_month.rename(columns={'Menu': 'Quantity'})
    fig_quantity_by_category_month = px.line(quantity_by_category_month, 
                                             x='Month_Number', 
                                             y='Quantity', 
                                             color='Category',
                                             title='Overall Quantity by Category',
                                             labels={'Month_Number': 'Month_Number', 'Quantity': 'Total Quantity Sold'},
                                            )
    fig_quantity_by_category_month.update_layout(xaxis=dict(title='Month'),
                                                 yaxis=dict(title='Total Quantity Sold'),
                                                 height=500,
                                                 width=850
                                                )
    st.plotly_chart(fig_quantity_by_category_month)

# Line Chart for Sales by Category
with col2:
    agg_price = df.groupby(['Month_Number', 'Category'], as_index=False)['Price'].sum()
    fig_sales_by_category_line = px.line(agg_price, 
                                         x='Month_Number', 
                                         y='Price', 
                                         color='Category',
                                         title='Overall Sales by Category',
                                         labels={'Category': 'Category', 'Price': 'Price', 'Month_Number': 'Month'},
                                      )
    fig_sales_by_category_line.update_layout(xaxis=dict(title='Month'),
                                              yaxis=dict(title='Sales'),
                                              height=500,
                                              width=850
                                            )
    st.plotly_chart(fig_sales_by_category_line)

# Add CSS to move col1 to the left
st.markdown(
    """
    <style>
    body {
        flex-direction: row;
    }
    div[data-testid="stHorizontalBlock"] > div:first-child {
        width: 33% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)



# Create 'Total Sales' column by multiplying 'Price' and 'Quantity'
df['Total Sales'] = df['Price'] * df['Quantity']

# Get the popular menu table
popular_menu = df['Menu'].value_counts().reset_index()
popular_menu.columns = ['Menu', 'Quantity Sold']

# Group by 'Menu' to get total sales for each menu
total_sales_by_menu = df.groupby('Menu')['Total Sales'].sum().reset_index()

# Merge popular_menu and total_sales_by_menu tables on 'Menu'
popular_menu = pd.merge(popular_menu, total_sales_by_menu, on='Menu')

# Round 'Total Sales' to 2 decimal places
popular_menu['Total Sales'] = popular_menu['Total Sales'].astype(int)



# set two columns layout
col1, col2 = st.columns(2)

# Specify the order of days of the week
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Reorder 'Day Of Week' based on the logical order (Monday to Friday)
df['Day Of Week'] = pd.Categorical(df['Day Of Week'],
                                   categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday','Saturday','Sunday'],
                                   ordered=True)

# Group by 'Day Of Week', 'Category' to get total sales for each day, category, and menu
quantity_by_day_and_category = df.groupby(['Day Of Week', 'Category']).agg({'Quantity': 'sum'}).reset_index()

# Display the popular menu table
with col1:
    st.write("**Top 5 Popular Menus**")
    popular_menu_display = popular_menu.head().reset_index(drop=True)
    popular_menu_display.index += 1  # เพิ่มลำดับ index ขึ้นต้นด้วย 1
    st.dataframe(popular_menu_display)

# ฺBar Chart for Quantity of Foods Sold by Day Of Week
with col2:
    fig_quantity_by_day_and_category = px.bar(quantity_by_day_and_category, 
                                          x='Day Of Week', 
                                          y='Quantity',
                                          color='Category',
                                          barmode='group',
                                          title='Quantity of Foods Sold by Day Of Week and Category',
                                          labels={'Day Of Week': 'Day Of Week', 'Quantity': 'Total Quantity Sold'},
                                          )
    fig_quantity_by_day_and_category.update_layout(xaxis=dict(title='Day Of Week'),
                                                yaxis=dict(title='Total Quantity Sold'),
                                                height=500,
                                                width=850
                                                )
    st.plotly_chart(fig_quantity_by_day_and_category)



# set two columns layout
col1, col2 = st.columns(2)

with col1:
# Create a bar chart for popular menu
    fig = px.bar(popular_menu, x='Menu', y='Quantity Sold', title='Quantity Sold by Menus',
             labels={'Menu': 'Menu', 'Quantity Sold': 'Quantity Sold'})
    st.plotly_chart(fig)


# Calculate Quantity Sold
df['Quantity Sold'] = df.groupby('Menu')['Menu'].transform('count')

# Get the top 3 popular menus in each category
top_menu_by_category = df.groupby(['Category', 'Menu'], as_index=False)['Quantity'].sum()
top_menu_by_category = top_menu_by_category.sort_values(by=['Category', 'Quantity'], ascending=[True, False])
top_menu_by_category = top_menu_by_category.groupby('Category').head(3)

with col2:
    fig_top_menu_by_category = px.bar(top_menu_by_category, 
                                  x='Menu', 
                                  y='Quantity', 
                                  color='Menu',
                                  facet_col='Category',
                                  title='Top 3 Popular Menus by Category',
                                  labels={'Menu': 'Menu', 'Quantity': 'Quantity'},
                                  height=500,
                                  width=850)
    fig_top_menu_by_category.update_layout(showlegend=False)  # Hide legend for individual facets
    st.plotly_chart(fig_top_menu_by_category)







# set two columns layout
col1, col2 = st.columns(2)

# Group by 'Date' and calculate average 'Time Taken to Serve' for each day
average_time_taken_by_day_of_week = df.groupby('Day Of Week')['Time Taken to Serve'].mean().reset_index()

# Bar Chart for Average Time Taken to Serve by Day Of Week
with col1:
    fig_time_taken_distribution = px.box(df, 
                                     x='Day Of Week', 
                                     y='Time Taken to Serve',
                                     title='Time Taken to Serve Distribution by Day Of Week',
                                     labels={'Day Of Week': 'Day Of Week', 'Time Taken to Serve': 'Time Taken to Serve (minutes)'},
                                     category_orders={'Day Of Week': day_order},
                                     points=False
                                     )
    fig_time_taken_distribution.update_layout(xaxis=dict(title='Day Of Week'),
                                          yaxis=dict(title='Time Taken to Serve (minutes)'),
                                          )
    st.plotly_chart(fig_time_taken_distribution)
    

# Box Plot for Time Taken to Serve Distribution by Day Of Week
with col2:
    fig_average_time_taken_by_day_of_week = px.bar(average_time_taken_by_day_of_week, 
                                               x='Day Of Week', 
                                               y='Time Taken to Serve',
                                               title='Average Time Taken to Serve by Day Of Week',
                                               labels={'Day Of Week': 'Day Of Week', 'Time Taken to Serve': 'Average Time Taken (minutes)'}
                                                )
    fig_average_time_taken_by_day_of_week.update_layout(xaxis=dict(title='Day Of Week'),
                                                    yaxis=dict(title='Average Time Taken (minutes)'),
                                                    height=500,
                                                    width=850
                                                    )
    st.plotly_chart(fig_average_time_taken_by_day_of_week)
    






# Assuming df is your DataFrame with the relevant columns
# Adjust this part based on your actual data structure
staff_count_by_day = df.groupby('Day Of Week')[['Kitchen Staff', 'Drinks Staff']].sum().reset_index()

# Melt the DataFrame to combine 'Kitchen Staff' and 'Drinks Staff' into a single column
staff_count_by_day_melted = staff_count_by_day.melt('Day Of Week', var_name='Staff Type', value_name='Staff Count')

# Create a bar chart
fig_staff_count_by_day = px.bar(staff_count_by_day_melted, 
                                x='Day Of Week', 
                                y='Staff Count', 
                                title='Staff Count by Day Of Week',
                                labels={'Day Of Week': 'Day Of Week', 'Staff Count': 'Staff Count', 'Staff Type': 'Staff Type'},
                                color='Staff Type',
                                barmode='group',
                                height=500,
                                width=850)  # Use barmode='group' to group bars by 'Staff Type'

# Show the figure
st.plotly_chart(fig_staff_count_by_day)












df.head()
df.info()
df.shape
df.tail()