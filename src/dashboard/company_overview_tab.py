from src.dashboard.dashboard_utils import *


def show_company_overview():
    st.header("Company Overview")

    st.markdown(
        f"""
        **Company:** {COMPANY_NAME}

        **Industry:** Enterprise software, cloud ERP, business AI, analytics, enterprise automation,
        and digital transformation.

        **Strategic focus areas:** SAP Business AI, Joule, SAP BTP, Cloud ERP, RISE with SAP,
        GROW with SAP, Autonomous Enterprise, customer transformation, risks, and market opportunities.
        """
    )

    show_repository_metrics()

    st.subheader("Repository Summary")
    show_repository_charts()

