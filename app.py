import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set up Streamlit configuration
st.set_page_config(layout='wide', page_title='Startup Analysis')

# Load the dataset once globally
df = pd.read_csv('startup_cleaned.csv')
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['month'] = df['Date'].dt.month
df['year'] = df['Date'].dt.year

# Handle missing values
df['investors'] = df['investors'].fillna('')
df['city'] = df['city'].fillna('')


# Function for displaying overall analysis
def load_overall_analysis():
    st.title("Overall Analysis")

    # Metrics
    total = round(df['amount'].sum())
    max_funding = df.groupby('Startup')['amount'].max().sort_values(ascending=False).head(1).values[0]
    avg_funding = round(df.groupby('Startup')['amount'].sum().mean())
    startup_number = df['Startup'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric('Total', f'{total} Cr')
    with col2:
        st.metric('Max', f'{max_funding} Cr')
    with col3:
        st.metric('Avg', f'{avg_funding} Cr')
    with col4:
        st.metric("Startups", str(startup_number))

    # MoM Graph
    st.header('MoM Graph')
    selected_option = st.selectbox('Select Type', ['Total', 'Count'])

    temp_df = df.groupby(['year', 'month'])['amount' if selected_option == 'Total' else 'amount'].agg(
        'sum' if selected_option == 'Total' else 'count').reset_index()
    temp_df['x_axis'] = temp_df['month'].astype(str) + '_' + temp_df['year'].astype(str)

    fig3, ax3 = plt.subplots(figsize=(12, 5))
    ax3.plot(temp_df['x_axis'], temp_df['amount'], marker='o', linestyle='-')
    ax3.set_xticks(temp_df['x_axis'])
    ax3.set_xticklabels(temp_df['x_axis'], rotation=45, ha='right')
    ax3.set_xlabel('Month_Year')
    ax3.set_ylabel('Investment Amount')
    ax3.set_title('Month-on-Month Investment Trend')

    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig3)


# Function for displaying investor details
def load_investor_details(investor):
    st.title(f"Investments by 💹 {investor}")

    # Load recent 5 investments
    filtered_df = df[df["investors"].str.contains(investor, case=False)]
    last5_df = filtered_df.sort_values(by="Date", ascending=False).head(5)[
        ["Date", "Startup", "Vertical", "city", "round", "amount"]]
    st.dataframe(last5_df)

    col1, col2, col3 = st.columns(3)

    with col1:
        # Biggest investment
        big_series = filtered_df.groupby('Startup')['amount'].sum().sort_values(ascending=False).head()
        st.subheader('Biggest Investment')
        fig, ax = plt.subplots()
        ax.bar(big_series.index, big_series.values)
        st.pyplot(fig)

    with col2:
        vertical_series = filtered_df.groupby('Vertical')['amount'].sum().sort_values(ascending=False)
        st.subheader('Sector Investment')
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series.values, labels=vertical_series.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)

    with col3:
        city_series = filtered_df.groupby('city')['amount'].sum().sort_values(ascending=False)
        st.subheader('City Investment Distribution')
        fig3, ax3 = plt.subplots()
        ax3.pie(city_series.values, labels=city_series.index, autopct='%1.1f%%', startangle=90)
        ax3.axis('equal')
        st.pyplot(fig3)

    cols1, cols2 = st.columns(2)

    with cols1:
        round_series = filtered_df.groupby('round')['amount'].sum().sort_values(ascending=False)
        st.subheader('Investment Round Distribution')
        fig4, ax4 = plt.subplots()
        ax4.pie(round_series.values, labels=round_series.index, autopct='%1.1f%%', startangle=90)
        ax4.axis('equal')
        st.pyplot(fig4)

    with cols2:
        year_series = filtered_df.groupby('year')['amount'].sum().sort_index()
        st.subheader('Yearly Investment Trends')
        fig5, ax5 = plt.subplots()
        ax5.plot(year_series.index, year_series.values, marker='o', linestyle='-', color='b')
        ax5.set_xlabel('Year')
        ax5.set_ylabel('Total Investment Amount')
        ax5.set_title(f'Yearly Investments by {investor}')
        ax5.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig5)


# Function to display startup funding details
def start_funding():
    missing_df = df.dropna(subset=['Startup', 'city'])
    startup_list = sorted(missing_df['Startup'].unique())

    select_startup = st.sidebar.selectbox('Select a Startup:', startup_list)
    startup_info = missing_df[missing_df['Startup'] == select_startup]
    # start_name=list(df['Startup'])
    if startup_list:
        start_name = list(df['Startup'])
        st.title(start_name)

    if not startup_info.empty:
        startup_city = startup_info['city']
        st.subheader(f"Startup City: {startup_city}")
    else:
        st.warning("City information not found for this startup.")


# Sidebar selection and button logic
st.sidebar.title('Startup Funding Analysis')
option = st.sidebar.selectbox('Select One', ['Overall Analysis', 'StartUp', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'StartUp':
    btn1 = st.sidebar.button('Find StartUp Details')
    if btn1:
        st.title("Startup Details")
        start_funding()

else:
    sorted_investors = list(
        sorted(set(investor.strip() for sublist in df['investors'].dropna().str.split(',') for investor in sublist)))
    selected_investor = st.sidebar.selectbox('Select Investor', sorted_investors)
    btn2 = st.sidebar.button('Find Investor Details')
    if btn2:
        load_investor_details(selected_investor)
