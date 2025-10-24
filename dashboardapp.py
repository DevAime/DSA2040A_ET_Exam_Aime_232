"""
DSA 2040A - Interactive Airbnb Analytics Dashboard
Student: [Your Name] - [Your ID]
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Airbnb NYC Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {
        color: #FF5A5F;
        font-weight: 700;
    }
    h2 {
        color: #484848;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# Cache data loading for performance
@st.cache_data
def load_data():
    """Load the transformed dataset"""
    try:
        df = pd.read_csv('transformed/transformed_full.csv')
        # Convert date column if exists
        if 'last_review' in df.columns:
            df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found! Please ensure 'transformed/transformed_full.csv' exists.")
        return None

# Load data
df = load_data()

if df is not None:
    # ========== HEADER ==========
    st.title("🏠 Airbnb NYC Analytics Dashboard")
    st.markdown("### Interactive Data Exploration & Business Intelligence")
    st.markdown("---")
    
    # ========== SIDEBAR FILTERS ==========
    st.sidebar.header("🔍 Filters")
    st.sidebar.markdown("Customize your analysis:")
    
    # Neighbourhood filter
    neighbourhoods = ['All'] + sorted(df['neighbourhood_group'].dropna().unique().tolist())
    selected_neighbourhood = st.sidebar.selectbox(
        "Neighbourhood Group",
        neighbourhoods,
        help="Filter by NYC borough"
    )
    
    # Room type filter
    room_types = ['All'] + sorted(df['room_type'].dropna().unique().tolist())
    selected_room_type = st.sidebar.selectbox(
        "Room Type",
        room_types,
        help="Filter by property type"
    )
    
    # Price range filter
    price_min = float(df['price'].min())
    price_max = float(df['price'].quantile(0.99))  # Use 99th percentile to avoid outliers
    selected_price_range = st.sidebar.slider(
        "Price Range ($)",
        min_value=price_min,
        max_value=price_max,
        value=(price_min, price_max),
        help="Filter by nightly price"
    )
    
    # Host experience filter
    host_exp_options = ['All'] + sorted(df['host_experience'].dropna().unique().tolist())
    selected_host_exp = st.sidebar.selectbox(
        "Host Experience",
        host_exp_options,
        help="Filter by host experience level"
    )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_neighbourhood != 'All':
        filtered_df = filtered_df[filtered_df['neighbourhood_group'] == selected_neighbourhood]
    
    if selected_room_type != 'All':
        filtered_df = filtered_df[filtered_df['room_type'] == selected_room_type]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= selected_price_range[0]) & 
        (filtered_df['price'] <= selected_price_range[1])
    ]
    
    if selected_host_exp != 'All':
        filtered_df = filtered_df[filtered_df['host_experience'] == selected_host_exp]
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Showing:** {len(filtered_df):,} / {len(df):,} listings")
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset All Filters"):
        st.experimental_rerun()
    
    # ========== KEY METRICS ==========
    st.header("📊 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Listings",
            value=f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df):,}" if len(filtered_df) != len(df) else None
        )
    
    with col2:
        avg_price = filtered_df['price'].mean()
        st.metric(
            label="Avg Price/Night",
            value=f"${avg_price:.2f}",
            delta=f"${avg_price - df['price'].mean():.2f}" if len(filtered_df) != len(df) else None
        )
    
    with col3:
        total_reviews = filtered_df['number_of_reviews'].sum()
        st.metric(
            label="Total Reviews",
            value=f"{total_reviews:,}",
            delta=None
        )
    
    with col4:
        avg_availability = filtered_df['availability_365'].mean()
        st.metric(
            label="Avg Availability",
            value=f"{avg_availability:.0f} days",
            delta=None
        )
    
    with col5:
        unique_hosts = filtered_df['host_id'].nunique()
        st.metric(
            label="Unique Hosts",
            value=f"{unique_hosts:,}",
            delta=None
        )
    
    st.markdown("---")
    
    # ========== MAIN VISUALIZATIONS ==========
    
    # Tab layout for different analysis sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Geographic Analysis", 
        "💰 Pricing Insights", 
        "⭐ Review Analytics",
        "🏢 Host Intelligence",
        "📈 Market Trends"
    ])
    
    # ========== TAB 1: GEOGRAPHIC ANALYSIS ==========
    with tab1:
        st.subheader("Geographic Distribution of Listings")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Interactive map
            fig_map = px.scatter_mapbox(
                filtered_df,
                lat='latitude',
                lon='longitude',
                color='price_category',
                size='price',
                hover_name='name',
                hover_data={
                    'price': ':$,.2f',
                    'room_type': True,
                    'neighbourhood': True,
                    'latitude': False,
                    'longitude': False
                },
                color_discrete_map={
                    'Budget': '#3498db',
                    'Economy': '#2ecc71',
                    'Mid-Range': '#f39c12',
                    'Premium': '#e74c3c',
                    'Luxury': '#9b59b6'
                },
                zoom=10,
                height=500,
                title="Listings Map by Price Category"
            )
            fig_map.update_layout(mapbox_style="open-street-map")
            fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
        
        with col2:
            # Neighbourhood distribution
            neighbourhood_counts = filtered_df['neighbourhood_group'].value_counts()
            
            fig_neighbourhood = go.Figure(data=[go.Pie(
                labels=neighbourhood_counts.index,
                values=neighbourhood_counts.values,
                hole=0.4,
                marker_colors=['#FF5A5F', '#00A699', '#FC642D', '#484848', '#767676']
            )])
            fig_neighbourhood.update_layout(
                title="Listings by Borough",
                height=250,
                margin=dict(t=40, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_neighbourhood, use_container_width=True)
            
            # Room type distribution
            room_counts = filtered_df['room_type'].value_counts()
            
            fig_room = go.Figure(data=[go.Pie(
                labels=room_counts.index,
                values=room_counts.values,
                hole=0.4,
                marker_colors=['#FF5A5F', '#00A699', '#FC642D']
            )])
            fig_room.update_layout(
                title="Listings by Room Type",
                height=250,
                margin=dict(t=40, b=0, l=0, r=0)
            )
            st.plotly_chart(fig_room, use_container_width=True)
    
    # ========== TAB 2: PRICING INSIGHTS ==========
    with tab2:
        st.subheader("Pricing Analysis & Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price distribution histogram
            fig_price_dist = px.histogram(
                filtered_df,
                x='price',
                nbins=50,
                title="Price Distribution",
                labels={'price': 'Price per Night ($)', 'count': 'Number of Listings'},
                color_discrete_sequence=['#FF5A5F']
            )
            fig_price_dist.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_price_dist, use_container_width=True)
        
        with col2:
            # Price by room type box plot
            fig_price_room = px.box(
                filtered_df,
                x='room_type',
                y='price',
                title="Price Distribution by Room Type",
                labels={'price': 'Price per Night ($)', 'room_type': 'Room Type'},
                color='room_type',
                color_discrete_sequence=['#FF5A5F', '#00A699', '#FC642D']
            )
            fig_price_room.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_price_room, use_container_width=True)
        
        # Price category breakdown
        st.markdown("### Price Category Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price category counts
            price_cat_counts = filtered_df['price_category'].value_counts().sort_index()
            
            fig_price_cat = go.Figure(data=[go.Bar(
                x=price_cat_counts.index,
                y=price_cat_counts.values,
                marker_color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'],
                text=price_cat_counts.values,
                textposition='outside'
            )])
            fig_price_cat.update_layout(
                title="Listings by Price Category",
                xaxis_title="Price Category",
                yaxis_title="Number of Listings",
                height=400
            )
            st.plotly_chart(fig_price_cat, use_container_width=True)
        
        with col2:
            # Average price by neighbourhood
            avg_price_neighbourhood = filtered_df.groupby('neighbourhood_group')['price'].mean().sort_values(ascending=False)
            
            fig_avg_price = go.Figure(data=[go.Bar(
                y=avg_price_neighbourhood.index,
                x=avg_price_neighbourhood.values,
                orientation='h',
                marker_color='#FF5A5F',
                text=[f'${x:.2f}' for x in avg_price_neighbourhood.values],
                textposition='outside'
            )])
            fig_avg_price.update_layout(
                title="Average Price by Borough",
                xaxis_title="Average Price ($)",
                yaxis_title="Borough",
                height=400
            )
            st.plotly_chart(fig_avg_price, use_container_width=True)
    
    # ========== TAB 3: REVIEW ANALYTICS ==========
    with tab3:
        st.subheader("Review Performance & Guest Engagement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Review activity distribution
            review_activity_counts = filtered_df['review_activity'].value_counts()
            
            fig_review_activity = go.Figure(data=[go.Pie(
                labels=review_activity_counts.index,
                values=review_activity_counts.values,
                hole=0.4,
                marker_colors=['#e74c3c', '#f39c12', '#2ecc71'],
                textinfo='label+percent',
                textposition='outside'
            )])
            fig_review_activity.update_layout(
                title="Review Activity Levels",
                height=400
            )
            st.plotly_chart(fig_review_activity, use_container_width=True)
        
        with col2:
            # Reviews by room type
            review_room_cross = filtered_df.groupby(['room_type', 'review_activity']).size().reset_index(name='count')
            
            fig_review_room = px.bar(
                review_room_cross,
                x='room_type',
                y='count',
                color='review_activity',
                title="Review Activity by Room Type",
                labels={'count': 'Number of Listings', 'room_type': 'Room Type'},
                color_discrete_map={'High': '#2ecc71', 'Medium': '#f39c12', 'Low': '#e74c3c'},
                barmode='group'
            )
            fig_review_room.update_layout(height=400)
            st.plotly_chart(fig_review_room, use_container_width=True)
        
        # Review volume analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Review volume tier distribution
            review_tier_counts = filtered_df['review_volume_tier'].value_counts().sort_index()
            
            fig_review_tier = go.Figure(data=[go.Bar(
                x=review_tier_counts.index,
                y=review_tier_counts.values,
                marker_color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
                text=review_tier_counts.values,
                textposition='outside'
            )])
            fig_review_tier.update_layout(
                title="Review Volume Tiers",
                xaxis_title="Tier",
                yaxis_title="Number of Listings",
                height=400
            )
            st.plotly_chart(fig_review_tier, use_container_width=True)
        
        with col2:
            # Scatter: Reviews vs Price
            fig_reviews_price = px.scatter(
                filtered_df.sample(min(1000, len(filtered_df))),  # Sample for performance
                x='number_of_reviews',
                y='price',
                color='review_activity',
                title="Reviews vs Price Relationship",
                labels={'number_of_reviews': 'Total Reviews', 'price': 'Price ($)'},
                color_discrete_map={'High': '#2ecc71', 'Medium': '#f39c12', 'Low': '#e74c3c'},
                opacity=0.6,
                height=400
            )
            st.plotly_chart(fig_reviews_price, use_container_width=True)
    
    # ========== TAB 4: HOST INTELLIGENCE ==========
    with tab4:
        st.subheader("Host Performance & Market Share")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Host experience distribution
            host_exp_counts = filtered_df['host_experience'].value_counts()
            
            fig_host_exp = go.Figure(data=[go.Pie(
                labels=host_exp_counts.index,
                values=host_exp_counts.values,
                hole=0.4,
                marker_colors=['#3498db', '#2ecc71', '#f39c12'],
                textinfo='label+percent',
                textposition='outside'
            )])
            fig_host_exp.update_layout(
                title="Host Experience Levels",
                height=400
            )
            st.plotly_chart(fig_host_exp, use_container_width=True)
        
        with col2:
            # Rental duration type distribution
            rental_duration_counts = filtered_df['rental_duration_type'].value_counts().sort_index()
            
            fig_rental_duration = go.Figure(data=[go.Bar(
                x=rental_duration_counts.index,
                y=rental_duration_counts.values,
                marker_color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c'],
                text=rental_duration_counts.values,
                textposition='outside'
            )])
            fig_rental_duration.update_layout(
                title="Rental Duration Strategy",
                xaxis_title="Duration Type",
                yaxis_title="Number of Listings",
                height=400
            )
            st.plotly_chart(fig_rental_duration, use_container_width=True)
        
        # Top hosts analysis
        st.markdown("### Top 10 Hosts by Listing Count")
        
        top_hosts = filtered_df.groupby('host_name').agg({
            'id': 'count',
            'price': 'mean',
            'number_of_reviews': 'sum',
            'availability_365': 'mean'
        }).sort_values('id', ascending=False).head(10).reset_index()
        
        top_hosts.columns = ['Host Name', 'Total Listings', 'Avg Price', 'Total Reviews', 'Avg Availability']
        top_hosts['Avg Price'] = top_hosts['Avg Price'].apply(lambda x: f'${x:.2f}')
        top_hosts['Avg Availability'] = top_hosts['Avg Availability'].apply(lambda x: f'{x:.0f} days')
        
        st.dataframe(top_hosts, use_container_width=True, hide_index=True)
        
        # Host experience vs pricing
        col1, col2 = st.columns(2)
        
        with col1:
            avg_price_by_exp = filtered_df.groupby('host_experience')['price'].mean().sort_values(ascending=False)
            
            fig_price_exp = go.Figure(data=[go.Bar(
                y=avg_price_by_exp.index,
                x=avg_price_by_exp.values,
                orientation='h',
                marker_color='#FF5A5F',
                text=[f'${x:.2f}' for x in avg_price_by_exp.values],
                textposition='outside'
            )])
            fig_price_exp.update_layout(
                title="Avg Price by Host Experience",
                xaxis_title="Average Price ($)",
                yaxis_title="Host Experience",
                height=350
            )
            st.plotly_chart(fig_price_exp, use_container_width=True)
        
        with col2:
            # New vs established listings
            new_listings_pct = (filtered_df['is_new_listing'].sum() / len(filtered_df)) * 100
            established_pct = 100 - new_listings_pct
            
            fig_new_listings = go.Figure(data=[go.Pie(
                labels=['Established Listings', 'New Listings (0 Reviews)'],
                values=[established_pct, new_listings_pct],
                marker_colors=['#2ecc71', '#e74c3c'],
                textinfo='label+percent',
                hole=0.4
            )])
            fig_new_listings.update_layout(
                title="New vs Established Listings",
                height=350
            )
            st.plotly_chart(fig_new_listings, use_container_width=True)
    
    # ========== TAB 5: MARKET TRENDS ==========
    with tab5:
        st.subheader("Market Trends & Availability Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Availability category distribution
            avail_cat_counts = filtered_df['availability_category'].value_counts().sort_index()
            
            fig_avail_cat = go.Figure(data=[go.Bar(
                x=avail_cat_counts.index,
                y=avail_cat_counts.values,
                marker_color=['#e74c3c', '#f39c12', '#2ecc71', '#3498db'],
                text=avail_cat_counts.values,
                textposition='outside'
            )])
            fig_avail_cat.update_layout(
                title="Availability Distribution",
                xaxis_title="Availability Category",
                yaxis_title="Number of Listings",
                height=400
            )
            st.plotly_chart(fig_avail_cat, use_container_width=True)
        
        with col2:
            # Price vs Availability relationship
            fig_price_avail = px.scatter(
                filtered_df.sample(min(1000, len(filtered_df))),
                x='availability_365',
                y='price',
                color='price_category',
                title="Price vs Availability Relationship",
                labels={'availability_365': 'Availability (days/year)', 'price': 'Price ($)'},
                color_discrete_map={
                    'Budget': '#3498db',
                    'Economy': '#2ecc71',
                    'Mid-Range': '#f39c12',
                    'Premium': '#e74c3c',
                    'Luxury': '#9b59b6'
                },
                opacity=0.6,
                height=400
            )
            st.plotly_chart(fig_price_avail, use_container_width=True)
        
        # Market composition
        st.markdown("### Market Composition Matrix")
        
        # Create heatmap of room type vs neighbourhood
        market_matrix = pd.crosstab(
            filtered_df['neighbourhood_group'],
            filtered_df['room_type']
        )
        
        fig_matrix = go.Figure(data=go.Heatmap(
            z=market_matrix.values,
            x=market_matrix.columns,
            y=market_matrix.index,
            colorscale='YlOrRd',
            text=market_matrix.values,
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Listings")
        ))
        fig_matrix.update_layout(
            title="Listings Distribution: Borough vs Room Type",
            xaxis_title="Room Type",
            yaxis_title="Borough",
            height=400
        )
        st.plotly_chart(fig_matrix, use_container_width=True)
        
        # Summary statistics table
        st.markdown("### Summary Statistics by Neighbourhood Group")
        
        summary_stats = filtered_df.groupby('neighbourhood_group').agg({
            'id': 'count',
            'price': ['mean', 'median'],
            'number_of_reviews': 'mean',
            'availability_365': 'mean',
            'reviews_per_month': 'mean'
        }).round(2)
        
        summary_stats.columns = ['Total Listings', 'Avg Price', 'Median Price', 
                                 'Avg Reviews', 'Avg Availability', 'Avg Reviews/Month']
        summary_stats = summary_stats.reset_index()
        
        st.dataframe(summary_stats, use_container_width=True, hide_index=True)
    
    # ========== DATA EXPLORER ==========
    st.markdown("---")
    st.header("🔍 Data Explorer")
    st.markdown("Browse and search the filtered dataset")
    
    # Search functionality
    search_term = st.text_input("🔎 Search listings by name or neighbourhood:", "")
    
    if search_term:
        search_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False, na=False) |
            filtered_df['neighbourhood'].str.contains(search_term, case=False, na=False)
        ]
    else:
        search_df = filtered_df
    
    # Select columns to display
    display_columns = ['name', 'neighbourhood_group', 'neighbourhood', 'room_type', 
                      'price', 'price_category', 'number_of_reviews', 'review_activity',
                      'availability_365', 'host_experience']
    
    st.dataframe(
        search_df[display_columns].head(100),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown(f"**Showing:** {min(100, len(search_df))} of {len(search_df):,} listings")
    
    # Download filtered data
    st.markdown("### 📥 Download Filtered Data")
    
    csv = search_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f"airbnb_filtered_data_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )
    
    # ========== FOOTER ==========
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #767676; padding: 20px;'>
        <p><strong>DSA 2040A - Data Warehousing & Mining</strong></p>
        <p>Interactive Dashboard | Built with Streamlit & Plotly | Data: Inside Airbnb</p>
        <p style='font-size: 12px;'>Student: [Your Name] | ID: [Your ID] | © 2025</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("Unable to load data. Please check that the transformed data file exists.")
    st.info("Expected file: `transformed/transformed_full.csv`")