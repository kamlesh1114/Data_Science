
import pandas as pd
import streamlit as st
import datetime as dt
from datetime import datetime
from io import BytesIO
import xlsxwriter

import streamlit_authenticator as stauth

import database as db

## Read excel and define df as required
st.set_page_config(page_title='Dashboard', page_icon=":bar_chart:", layout="wide", initial_sidebar_state="auto",menu_items={'Get help':"https://www.kreditbee.in",'Report a bug': "https://www.kreditbee.in",'About': "# This is a header. This is an *extremely* cool app!"})
st.sidebar.image("kblogo.png", use_column_width=True)

users=db.fetch_users()

usernames=[user["key"] for user in users]
names=[user["name"] for user in users]
hashed_passwords=[user["password"] for user in users]
authenticator=stauth.Authenticate(names,usernames,hashed_passwords,"dsa_dashboard","xyzab",cookie_expiry_days=30)

name,authentication_status, username=authenticator.login("Login","sidebar")

if authentication_status== False:
    st.error("Username/Password is Incorrect")

if authentication_status== None:
    st.warning("Please Enter Your Usernames and Password")

if authentication_status==True:
    if st.session_state["authentication_status"]==True:
        st.sidebar.write(f' **Mr. {st.session_state["name"]}**')
        authenticator.logout('Logout', 'sidebar')
        # st.title('Some content')

    month=datetime.today().strftime('%B')
    ### 31 days Months list
    list1=['January', 'March', 'May', 'July', 'August', 'October','December']
    ### 30 days Months list
    list2=['November', 'April', 'June','September']
    # all_months=['January','February','March','April','May','June','July','August','September','October','November','December']
    all_months=[12,11,10,9,8,7,6,5,4,3,2,1]

    list1_2=[1, 3, 5, 7, 8, 10,12]  ## 31 days
    list2_1=[11, 4, 6,9]  ## 30 days

    # using now() to get current time 
    current_time = dt.datetime.now()
    t=current_time.day
    m=current_time.month

    option_month = st.sidebar.selectbox(
        'Select Month:',
        (all_months))
    # st.sidebar.write('You selected:', option_month)
    months_list=option_month

    if option_month in list2_1:
        kk=30
        months_list=option_month

    elif option_month in list1_2:
        kk=31
        months_list=option_month
        if months_list==m:
            if 1<t<10:
                kk=t-1
            else:
                kk=t-1
            
    date_list=[]
    for i in range(kk+1):
        if i<=8:
            opt_list1=(f"2022-{months_list}-{0}{1+i}")
            date_list.append(opt_list1)
        elif i>=10:
            opt_list2=(f"2022-{months_list}-{i}")
            date_list.append(opt_list2)

    # st.header('DSA Live Tracker Dashboard')

    dsa_wise=pd.read_excel(f'Report_New_{kk}_{months_list}.xlsx',sheet_name=0,index_col=False)    
    bdm_wise=pd.read_excel(f'Report_New_{kk}_{months_list}.xlsx',sheet_name=1)
    loan_leads=pd.read_excel(f'Report_New_{kk}_{months_list}.xlsx',sheet_name=2)
    user_counts=pd.read_excel(f'Report_New_{kk}_{months_list}.xlsx',sheet_name=3)


    dsa_reg_list=user_counts['current_attributed_channel'].unique()

    # loan_leads.drop(['mobile'],axis=1,inplace=True)
    # user_counts.drop(['mobile'],axis=1,inplace=True)

    ## Daywise latest loans and gmv df

    daywise1=bdm_wise.T
    daywise2=daywise1.drop(['BDM']).drop(daywise1.columns[[0,1,2,3,4,5]],axis=1).T
    daywise=daywise2.drop(daywise2.iloc[:,4::],axis=1)



    ## Counts and sum of required infor (i.e information in card)
    reg_list=[]
    for g in range(len(dsa_reg_list)):
        reg_df=(user_counts[user_counts['current_attributed_channel'].isin([dsa_reg_list[g]])].groupby('registration_date')['uid'].count()).astype(int)
        reg_list.append(reg_df)

    ## making final df of registrations for visualization

    ##particular date wise filter
    
    date1=[]
    for d in range(kk):
        date1.append(1+d)
    
    date_option1=st.selectbox(
            'Select Date:',['All']+(date1))
    
    if date_option1=='All':
        final_date=date_list
    else:
        final_date=[date_list[date_option1-1]]
    
    final_reg_df=pd.DataFrame(reg_list,columns=final_date,index=dsa_reg_list)

#   common df for loans and gmv counts

    common_df=loan_leads[loan_leads['first_loan_taken_date'].isin(final_date)]


    final_reg_df.loc["Total"]=final_reg_df.sum(numeric_only=False)
    final_reg_df["Total"]=final_reg_df.sum(numeric_only=True,axis=1)

    all_reg_count=user_counts[user_counts['registration_date'].isin(final_date)]['uid'].count()

    all_loan_count=common_df['uid'].count()
    all_gmv=common_df['first_loan_gmv'].sum()

    all_se_count=common_df[common_df['product_name'].isin(['MLA-X'])]['uid'].count()
    all_se_gmv=common_df[common_df['product_name'].isin(['MLA-X'])]['first_loan_gmv'].sum()

    all_sa_count=common_df[common_df['product_name'].isin(['PK-SA'])]['uid'].count()
    all_sa_gmv=common_df[common_df['product_name'].isin(['PK-SA'])]['first_loan_gmv'].sum()

    all_ats=round(all_gmv/all_loan_count)


    df = pd.DataFrame({
      'first column': [1, 2, 3, 4],
      'second column': [10, 20, 30, 40]
    })


    ## Selectbox execution data in sidebar
    option = st.sidebar.selectbox(
        'Select Here:',
        ('Summary','BDM WISE', 'DSA WISE'))

        
    ## Report downloading dataframe
    st.sidebar.write(f'Report Upto: {kk}-{months_list}-2022')
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        dsa_wise.to_excel(writer, index=False, sheet_name='dsa')
        bdm_wise.to_excel(writer, index=False, sheet_name='bdm')
        loan_leads.to_excel(writer, index=False, sheet_name='loan_leads')
        user_counts.to_excel(writer, index=False, sheet_name='user_counts')
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    df_xlsx = to_excel(df)

    st.sidebar.download_button(label='📥 Download Final Report',
                                    data=df_xlsx ,
                                    file_name= f"Report_New_{kk}_{months_list}.xlsx")


    ## Card design and data inserting
    import hydralit_components as hc

    if option=='BDM WISE':
        """
        #### BDM WISE SALES:
        """
        st.write(bdm_wise)

    elif option=='DSA WISE':
        """
        #### DSA WISE SALES:
        """
        st.write(dsa_wise)

    elif option=='Summary':
        expander7 = st.expander("Latest Counts Here")
        expander7.table(daywise)

        #can apply customisation to almost all the properties of the card, including the progress bar
    #     color_library=[533483,E94560,   used now  FB2576,3F0071, 524A4E]

        ## Target Condition (all gmv loans,reg etc) should be month wise
       
        ### added on 3-12-2022

        target_2022={'Jan-2022':20000000,'Feb-2022':30000000,'March-2022':320000000,'Apr-2022':56000000,'May-2022':450000000
                    ,'June-2022':500000000,'July-2022':550000000,'August-2022':53000000,'Sep-2022':71000000
                    ,'October-2022':65000000,'November-2022':33000000,'Dec-2022':45600000}

        # target_dict_2023={'Jan-2023':50000000,'Feb-2023':50000000,'March-2023':50000000,'Apr-2023':50000000,'May-2023':50000000,
        #                   'June-2023':50000000,'July-2023':50000000,'August-2023':50000000,'Sep-2023':50000000
        #                   ,'October-2023':50000000,'November-2023':50000000,'Dec-2023':50000000}
        
        reg_target=17000                                    
        reg_achieve=(all_reg_count/reg_target)*100
        
        target_list=list(target_2022.values())
        target=target_list[months_list-1]
        gmv_achieve=(all_gmv/target)*100

# ## THEMES FOR INDIVIDUAL CARDS
#         theme_bad = {'bgcolor': '#FFF0F0','title_color': 'red','content_color': 'red'}
#         theme_neutral = {'bgcolor': '#FCFEFC','title_color': '#3CCF4E','content_color':'#3CCF4E'}   ## Theme for achieved target
#         theme_neutral1 = {'bgcolor': '#7A4069','title_color': '#ffff02','content_color':'white'}  ## Theme for general
#         theme_good = {'bgcolor': '#fff5fe','title_color': 'green','content_color': 'green','icon_color': 'green', 'icon': 'fa fa-check-  circle'}

#         ### added on 3-12-2022
#         if reg_achieve>=90:
#             theme1=theme_neutral
#         else:
#             theme1=theme_bad

#         ## Sentiments color setting condition
#         if gmv_achieve>=80:
#             theme=theme_neutral
#         else:
#             theme=theme_bad
        
        ## Arrow sign conditions
        #  st.metric(label="Temperature", value="70 °F", delta="1.2 °F")

        """
        ##### Business Done Till Selected Month/Day
        
        """
        col1, col2, col3,col4= st.columns(4)
        col1.metric("Overall GMV", str(f'{round((all_gmv/10000000),2)}Cr'),(f'Achieved : {round(gmv_achieve)}%'))
        col2.metric('Overall Loans',all_loan_count)
        col3.metric('Average Ticket Size',str(f'{(all_ats)}'))
        col4.metric("Overall Registration",str(f'{(all_reg_count)}'), (f'Achieved: {round(reg_achieve)}%'))
        
        col5,col6,col7,col8= st.columns(4)
        col5.metric("Salary Advance GMV", str(f'{round((all_sa_gmv/10000000),2)}Cr'))
        col6.metric('SA Loans',all_sa_count)
        col7.metric('Self Employed GMV', str(f'{round((all_se_gmv/10000000),2)}Cr'))
        col8.metric("SE Loans",str(f'{(all_se_count)}'))

        """ 
        ##### Expected Business In Current Month
        
        """
        exp_loan_leads=pd.read_excel(f'Report_New_{t-1}_{m}.xlsx',sheet_name=2)
        exp_all_gmv=exp_loan_leads['first_loan_gmv'].sum()
        exp_all_loans=exp_loan_leads['uid'].count()

        ## Arrow condition ------------------ To be added

        exp_gmv=round(((exp_all_gmv/(t-1))*30),2)
        exp_target=target_list[m-1]
        exp_gmv_achieve=(exp_gmv/exp_target)*100

        col9,col10,col11,col12= st.columns(4)
        col9.metric("Expected Overall GMV",str(f'{round(((exp_all_gmv/(t-1))*30/10000000),2)}Cr'),(f'Expected : {round(exp_gmv_achieve)}%'))
        col10.metric("Expected Overall Loans",str(f'{round((exp_all_loans/(t-1))*30)}'))
        col11.metric("Average Daily GMV",str(f'{round(((exp_all_gmv/(t-1))/10000000),2)}Cr'))
        col12.metric("Average Daily loans",str(f'{round(exp_all_loans/(t-1))}'))

    #     cc = st.columns(4)
    #     with cc[0]:

    #      # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
    #         hc.info_card(title=str(f'{round((all_gmv/10000000),2)}Cr'), content=(f'Overall GMV {round(gmv_achieve)}%'),theme_override=theme)

    #     with cc[1]:
    #         hc.info_card(title=str(all_loan_count), content='Total Loans',theme_override=theme)

    #     with cc[2]:
    #         hc.info_card(title=str(f'{(all_ats)}'), content='ATS',theme_override=theme)
    #     with cc[3]:
    #      #customise the the theming for a neutral content
    #         hc.info_card(title=str(f'{(all_reg_count)}'),content=(f'Registrations {round(reg_achieve)}%'),theme_override=theme1)
    # #   st.write(dsa_wise)
    #     theme_neutral = {'bgcolor': '#F4EEED','title_color': '#fdd535','content_color': 'white'}

    #     cd = st.columns(4)
    #     with cd[0]:

    #      # can just use 'good', 'bad', 'neutral' sentiment to auto color the card
    #         hc.info_card(title=str(f'{round((all_sa_gmv/10000000),2)}Cr'), content='SA GMV',theme_override=theme)

    #     with cd[1]:
    #         hc.info_card(title=str(all_sa_count), content='SA Count',theme_override=theme)

    #     with cd[2]:
    #         hc.info_card(title=str(all_se_count),content='SE Count',theme_override=theme)

    #     with cd[3]:
    #      #customise the the theming for a neutral content
    #         hc.info_card(title=str(f'{round((all_se_gmv/10000000),2)}Cr'), content='SE GMV',theme_override=theme)
    
        
    if date_option1=='All':
        comment=(f'Till  {kk}-{months_list}')
    else:
        comment=(f'{date_list[date_option1-1]}')
    
    st.sidebar.write('You Selected Date :',comment)
    
    expander1 = st.expander("Top5 DSA See Here")
    expander1.write(dsa_wise.sort_values(by=['TOTAL_GMV'],ascending=False).head(6).dropna(axis=0).drop(dsa_wise.iloc[:,8::], axis=1).drop('BDM',axis=1))
    

    import time

    dtcus_df_reg_dsa=user_counts[user_counts['registration_date'].isin(final_date)]
    dsawise_reg_date=dtcus_df_reg_dsa.groupby('registration_date')['current_attributed_channel'].count()
    
    dsa_loans_datewise=common_df.groupby('current_attributed_channel')['uid'].count()
    dsa_gmv_datewise=common_df.groupby('current_attributed_channel')['first_loan_gmv'].sum()
    
    datewise_gmv_all=common_df.groupby('first_loan_taken_date')['first_loan_gmv'].sum()
    datewise_loans_all=common_df.groupby('first_loan_taken_date')['uid'].count()

## Added this on 3-12-2022
    expander8 = st.expander("Date-Wise gmv")
    expander8.area_chart(datewise_gmv_all)

    expander9 = st.expander("Date-Wise loans")
    expander9.area_chart(datewise_loans_all)
#----------------------------------------------

    expander2 = st.expander("GMV DSA-Wise on Selected Date")
    expander2.bar_chart(dsa_gmv_datewise)
 
    expander3 = st.expander("Loans DSA-Wise on Selected Date")
    expander3.bar_chart(dsa_loans_datewise)
    
    
    if date_option1=='All':
       
        expander4 = st.expander("Date Wise Registrations on selected date")
        expander4.area_chart(dsawise_reg_date)
    else:
        pass

    expander5 = st.expander("DSA Wise Registrations on selected date")

    dtcus_df_reg_dsa=user_counts[user_counts['registration_date'].isin(final_date)]
    dsawise_reg=dtcus_df_reg_dsa.groupby('current_attributed_channel')['registration_date'].count()
    
    expander5.bar_chart(dsawise_reg)
    
    # final_reg_df.sort_values(['Total'])
    
    final_reg_df.sort_values(by=['Total'],ascending=False)
    final_reg_df = final_reg_df.style.highlight_null(props="color:Transparent;")  # hide NaNs
    # final_reg_df.round(decimals =0)
    
    expander6 = st.expander("Registrations Table on Selected Date")
    expander6.write(final_reg_df)
