import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import requests

API_KEY = "capstone"
API_BASE_URL = "https://api-dot-projectcapstone-376415.oa.r.appspot.com"

def load_data(response_json):
    try:
        data = pd.json_normalize(response_json, "result")
    except Exception as e:
        print(e)
        data = pd.DataFrame()
    return data

def get_session_state():
    return st.session_state


class SessionState:
    def __init__(self):
        self.logged_in = False
        self.username = None

def login(username, password):
    response = requests.post(f"{API_BASE_URL}/api/v4/login", json={"username": username, "password": password}, headers={"x-api-key": API_KEY})
    if response.status_code == 200:
        return True
    return False

def register(username, password):
    response = requests.post(f"{API_BASE_URL}/api/v4/register", json={"username": username, "password": password}, headers={"x-api-key": API_KEY})
    if response.status_code == 201:
        return True
    return False

def login_or_register_page():
    st.title("Authentication")
    st.subheader("Please log in or register")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Log In")
    register_button = st.button("Register")

    if login_button:
        if login(username, password):
            return username
        else:
            st.error("Invalid credentials")

    if register_button:
        if register(username, password):
            st.success("Registered successfully. Please log in with your credentials.")
        else:
            st.error("Registration failed")
    return None


def main_app():
    st.title("H&M KPI's") 
    selected_data_category = st.sidebar.selectbox("Select a category to explore:", ["General Information", "Revenue/APV"])

    if selected_data_category == "General Information":
        # Fetch and load data from the API URLs
        response = requests.get("https://api-dot-projectcapstone-376415.oa.r.appspot.com/api/v1/customers", headers={"x-api-key": API_KEY})
        response_json = response.json()
        customers_df = load_data(response_json)


        response = requests.get("https://api-dot-projectcapstone-376415.oa.r.appspot.com/api/v2/articles", headers={"x-api-key": API_KEY})
        response_json = response.json()
        articles_df = load_data(response_json)

        response = requests.get("https://api-dot-projectcapstone-376415.oa.r.appspot.com/api/v3/transactions/ageandclub", headers={"x-api-key": API_KEY})
        response_json = response.json()
        transactions_df = load_data(response_json)

        #Filter 1: select age range 
        age_range = st.sidebar.slider("Select Age Range:", min_value=0, max_value=100, value=(0, 100), step=1)

        #Filter 2: select sales channel
        sales_channels_lst = transactions_df["sales_channel_id"].unique().tolist()
        selected_sales_channel = st.sidebar.multiselect("Select Sales Channel(s):", sales_channels_lst, default=sales_channels_lst)

        #Filter 3: select club member status
        club_member_status_lst = customers_df["club_member_status"].unique().tolist()
        selected_club_member_status = st.sidebar.multiselect(
            label="Select Club Member Status:",
            options=club_member_status_lst,
            default=club_member_status_lst,
            key="multiselect_club_member_status"
        )

        #Apply the filters to the dataframes

        #Filtered based on age
        filtered_age_customers_df = customers_df[(customers_df["age"] >= age_range[0]) & (customers_df["age"] <= age_range[1])]
        #Filtered based on club status
        filtered_club_customers_df = customers_df[customers_df["club_member_status"].isin(selected_club_member_status)]
        ##Filtered based on age and club status 
        filtered_club_age_customers_df = filtered_age_customers_df[filtered_age_customers_df["club_member_status"].isin(selected_club_member_status)]

        #Filtered based on age, club status and sale channel
        filtered_transactions_df = transactions_df[transactions_df["sales_channel_id"].isin(selected_sales_channel)]
        filtered_transactions_df = filtered_transactions_df[(filtered_transactions_df["age"] >= age_range[0]) & (customers_df["age"] <= age_range[1])]
        filtered_transactions_df = filtered_transactions_df[filtered_transactions_df["club_member_status"].isin(selected_club_member_status)]


        # KPI: customers
        st.subheader("Customer Information by age and club membership :")
        st.write("---")

        # Create columns for displaying the KPIs
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Number of customers:**", unsafe_allow_html=True)
            st.write(filtered_club_age_customers_df["customer_id"].nunique())

        with col2:
            st.markdown("**Average age:**", unsafe_allow_html=True)
            st.write(round(filtered_club_age_customers_df["age"].mean(), 1))

        with col3:
            st.markdown("**Age range:**", unsafe_allow_html=True)
            st.write(f"{round(filtered_club_age_customers_df['age'].min(), 1)} - {round(filtered_club_age_customers_df['age'].max(), 1)}")

        st.write("\n")

        # Create columns for displaying the club member status percentages by age filter
        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown("**Percentage of Active members:**", unsafe_allow_html=True)
            st.write(f"{(filtered_age_customers_df['club_member_status'] == 'ACTIVE').mean() * 100:.1f}%")

        with col5:
            st.markdown("**Percentage of Pre-create members:**", unsafe_allow_html=True)
            st.write(f"{(filtered_age_customers_df['club_member_status'] == 'PRE-CREATE').mean() * 100:.1f}%")

        with col6:
            st.markdown("**Percentage of Left club members:**", unsafe_allow_html=True)
            st.write(f"{(filtered_age_customers_df['club_member_status'] == 'LEFT CLUB').mean() * 100:.1f}%")

        st.write("\n")

        # Bar chart for displaying age groups
        age_intervals = ["15-35", "36-55", "56-75", "75-97"]
        age_counts = [
            ((filtered_club_customers_df['age'] >= 15) & (filtered_club_customers_df['age'] <= 35)).sum(),
            ((filtered_club_customers_df['age'] >= 36) & (filtered_club_customers_df['age'] <= 55)).sum(),
            ((filtered_club_customers_df['age'] >= 56) & (filtered_club_customers_df['age'] <= 75)).sum(),
            ((filtered_club_customers_df['age'] >= 75) & (filtered_club_customers_df['age'] <= 97)).sum()
        ]

        age_percentage = (age_counts / sum(age_counts)) * 100

        fig = go.Figure(go.Bar(
            x=age_intervals,
            y=age_counts,
            text=[f"{p:.1f}%" for p in age_percentage],
            textposition='auto'
        ))

        fig.update_layout(
            xaxis_title="Age Intervals",
            yaxis_title="Percentage"
        )

        st.plotly_chart(fig)
        st.subheader("")

            

        # KPI: transactions
        st.subheader("Transactions Information by channel, age and club:")
        st.write("---")

        col11, col12, col13, col14 = st.columns(4)

        with col11:
            st.markdown("**Num. of Transactions:**", unsafe_allow_html=True)
            st.write(f"{filtered_transactions_df['price'].nunique()}")

        with col12:
            st.markdown("**Average Price:**", unsafe_allow_html=True)
            st.write(f"${filtered_transactions_df['price'].mean():.3f}")

        with col13:
            st.markdown("**Max Price:**", unsafe_allow_html=True)
            st.write(f"${filtered_transactions_df['price'].max():.3f}")

        with col14:
            st.markdown("**Min Price:**", unsafe_allow_html=True)
            st.write(f"${filtered_transactions_df['price'].min():.3f}")

        st.write("\n")

        # KPI: Articles
        st.subheader("Articles Information:")
        st.write("---")

        col15, col16, col17 = st.columns(3)

        with col15:
            st.markdown("**Number of Male Articles:**", unsafe_allow_html=True)
            st.write(f"{articles_df['product_category'].value_counts()['Male']}")

        with col16:
            st.markdown("**Number of Female Articles:**", unsafe_allow_html=True)
            st.write(f"{articles_df['product_category'].value_counts()['Female']}")

        with col17:
            st.markdown("**Number of Baby Articles:**", unsafe_allow_html=True)
            st.write(f"{articles_df['product_category'].value_counts()['Baby']}")

        st.write("\n")

        # Articles graphs
        gender_counts = articles_df["product_category"].value_counts()
        gender_percentage = (gender_counts / gender_counts.sum()) * 100

        fig = go.Figure(go.Bar(
            x=gender_counts.index,
            y=gender_counts.values,
            text=[f"{p:.1f}%" for p in gender_percentage],
            textposition='auto'
        ))

        fig.update_layout(
            title="Number of Articles by Gender",
            xaxis_title="Gender",
            yaxis_title="Number of Articles"
        )

        st.plotly_chart(fig)
        st.write("\n")






    elif selected_data_category == "Revenue/APV":

        #For the revenue_df I have to merge transactions with articles_df(I need only product_group_name columns) and with customer_df(I need gender, club member status columns)
        # Fetch and load data from the API URLs
        response = requests.get("https://api-dot-projectcapstone-376415.oa.r.appspot.com/api/v3/transactions/ageandclub", headers={"x-api-key": API_KEY})
        response_json = response.json()
        transactions_by_age_and_club_df = load_data(response_json)

        response = requests.get("https://api-dot-projectcapstone-376415.oa.r.appspot.com/api/v3/transactions/productcategory", headers={"x-api-key": API_KEY})
        response_json = response.json()
        transactions_by_productcategory_df = load_data(response_json)

        #Filter1: channel
        sales_channels_lst = transactions_by_age_and_club_df["sales_channel_id"].unique().tolist()
        selected_sales_channel = st.sidebar.multiselect("Select Sales Channel(s):", sales_channels_lst, default=sales_channels_lst)

        #Filter 2: choose age
        age_range = st.sidebar.slider("Select Age Range:", min_value=0, max_value=100, value=(0, 100), step=1)


        #Filter 3: choose club member status
        club_member_status_lst = transactions_by_age_and_club_df["club_member_status"].unique().tolist()
        selected_club_member_status = st.sidebar.multiselect(
            label="Select Club Member Status:",
            options=club_member_status_lst,
            default=club_member_status_lst,
            key="multiselect_club_member_status"
        )

        # Filter 4: Choose product category
        product_category_lst = transactions_by_productcategory_df["product_category"].unique().tolist()
        selected_product_category = st.sidebar.multiselect(
            label="Select Product Category:",
            options=product_category_lst,
            default=product_category_lst,
            key="multiselect_product_category"
        )


        def apv_club_age(filtered_transactions_by_age_and_club_df):
            st.subheader('Apv by club member status and age')
            st.write("---")

            filtered_transactions_by_age_and_club_df = transactions_by_age_and_club_df[transactions_by_age_and_club_df["club_member_status"].isin(selected_club_member_status)]
            filtered_transactions_by_age_and_club_df = filtered_transactions_by_age_and_club_df[(filtered_transactions_by_age_and_club_df["age"] >= age_range[0]) & (filtered_transactions_by_age_and_club_df["age"] <= age_range[1])]

            total_revenue = filtered_transactions_by_age_and_club_df["price"].sum()

            num_unique_customers = round(filtered_transactions_by_age_and_club_df["customer_id"].nunique(), 3)
            num_transactions = round(filtered_transactions_by_age_and_club_df.shape[0], 3)

            if num_unique_customers > 0:
                APV = total_revenue / num_unique_customers
                purchase_frequency = num_transactions / num_unique_customers
            else:
                APV = 0
                purchase_frequency = 0

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Average Purchase Value (APV):**", unsafe_allow_html=True)
                st.write(f"${APV:.3f}")

            with col2:
                st.markdown("**Purchase Frequency:**", unsafe_allow_html=True)
                st.write(f"{purchase_frequency:.2f} transactions per customer")
        
        apv_club_age(transactions_by_age_and_club_df)

                
        def revenue_product_category(transactions_by_productcategory_df):
            st.subheader("")
            st.subheader('Revenue by product type:')
            st.write("---")

            filtered_transactions_by_product_category_df = transactions_by_productcategory_df[transactions_by_productcategory_df["product_category"].isin(selected_product_category)]

            revenue_by_product_category = filtered_transactions_by_product_category_df.groupby("product_category")["price"].sum()

            total_revenue = revenue_by_product_category.sum()

            col1, = st.columns(1) 

            with col1:
                st.markdown("**Total Revenue by Selected Product Categories:**", unsafe_allow_html=True)
                st.write(f"${total_revenue:.2f}")

            
            percentage_by_product_category = (revenue_by_product_category / total_revenue) * 100

            #displaying the revenue and percentage for each product category
            fig = go.Figure(go.Waterfall(
                name="Revenue",
                orientation="v",
                measure=["relative"] * len(revenue_by_product_category),
                x=revenue_by_product_category.index,
                y=revenue_by_product_category.values,
                textposition="outside",
                text=[f"${rev:,.0f} ({perc:.1f}%)" for rev, perc in zip(revenue_by_product_category, percentage_by_product_category)],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))

            fig.update_layout(
                title="Revenue by Product Category",
                xaxis_title="Product Category",
                yaxis_title="Revenue",
                showlegend=False,
            )

            st.plotly_chart(fig)

        revenue_product_category(transactions_by_productcategory_df)

        def revenue_age_club_channel(transactions_by_age_and_club_df):
            st.subheader("")
            st.subheader('Revenue by age, channel and club membership:')
            st.write("---")

            filtered_transactions_by_age_and_club_df = transactions_by_age_and_club_df[transactions_by_age_and_club_df["club_member_status"].isin(selected_club_member_status)]
            filtered_transactions_by_age_and_club_df = filtered_transactions_by_age_and_club_df[(filtered_transactions_by_age_and_club_df["age"] >= age_range[0]) & (filtered_transactions_by_age_and_club_df["age"] <= age_range[1])]
            filtered_transactions_by_age_and_club_df = filtered_transactions_by_age_and_club_df[filtered_transactions_by_age_and_club_df["sales_channel_id"].isin(selected_sales_channel)]

            total_revenue = filtered_transactions_by_age_and_club_df["price"].sum()
        
            col1, = st.columns(1)  

            with col1:
                st.markdown("**Total Revenue by age range, channel and club membership:**", unsafe_allow_html=True)
                st.write(f"${total_revenue:.2f}")


            revenue_by_club_member_status = filtered_transactions_by_age_and_club_df.groupby("club_member_status")["price"].sum()
            percentage_by_club_member_status = (revenue_by_club_member_status / total_revenue) * 100


            #displaying the revenue for each club member status
            fig1 = go.Figure(go.Waterfall(
                name="Revenue",
                orientation="v",
                measure=["relative"] * len(revenue_by_club_member_status),
                x=revenue_by_club_member_status.index,
                y=revenue_by_club_member_status.values,
                textposition="outside",
                text=[f"${rev:,.0f} ({pct:.1f}%)" for rev, pct in zip(revenue_by_club_member_status, percentage_by_club_member_status)],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))

            fig1.update_layout(
                title="Revenue by Club Member Status",
                xaxis_title="Club Member Status",
                yaxis_title="Revenue",
                showlegend=False,
            )

            st.plotly_chart(fig1)

            
            age_intervals = ["15-35", "36-55", "56-75", "75-97"]
            age_bins = [15, 36, 56, 75, 97]
            filtered_transactions_by_age_and_club_df["age_group"] = pd.cut(filtered_transactions_by_age_and_club_df["age"], bins=age_bins, labels=age_intervals, include_lowest=True)

            revenue_by_age_group = filtered_transactions_by_age_and_club_df.groupby("age_group")["price"].sum()
            percentage_by_age_group = (revenue_by_age_group / total_revenue) * 100


            #displaying the revenue for each age group
            fig2 = go.Figure(go.Waterfall(
                name="Revenue",
                orientation="v",
                measure=["relative"] * len(revenue_by_age_group),
                x=revenue_by_age_group.index,
                y=revenue_by_age_group.values,
                textposition="outside",
                text=[f"${rev:,.0f} ({pct:.1f}%)" for rev, pct in zip(revenue_by_age_group, percentage_by_age_group)],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))

            fig2.update_layout(
                title="Revenue by Age Group",
                xaxis_title="Age Group",
                yaxis_title="Revenue",
                showlegend=False,
            )

            st.plotly_chart(fig2)

            
            revenue_by_sales_channel = filtered_transactions_by_age_and_club_df.groupby("sales_channel_id")["price"].sum()
            percentage_by_sales_channel = (revenue_by_sales_channel / total_revenue) * 100

            #displaying the revenue for each sales channel
            fig3 = go.Figure(go.Waterfall(
                name="Revenue",
                orientation="v",
                measure=["relative"] * len(revenue_by_sales_channel),
                x=revenue_by_sales_channel.index,
                y=revenue_by_sales_channel.values,
                textposition="outside",
                text=[f"${rev:,.0f} ({pct:.1f}%)" for rev, pct in zip(revenue_by_sales_channel, percentage_by_sales_channel)],
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))

            fig3.update_layout(
                title="Revenue by Sales Channel",
                xaxis_title="Sales Channel",
                yaxis_title="Revenue",
                showlegend=False,
            )

            st.plotly_chart(fig3)


        revenue_age_club_channel(transactions_by_age_and_club_df)



def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        main_app()
    else:
        logged_in_username = login_or_register_page()
        if logged_in_username:
            st.session_state.logged_in = True
            st.session_state.username = logged_in_username
            st.success("Logged in successfully")
            st.experimental_rerun()

    return False

if __name__ == "__main__":
    main()


















        
        

        


    

    

    






    
    
   










    
    







    



