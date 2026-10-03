"""
create_tableau_twb.py

Generates a Tableau Workbook (.twb) XML file configured for Tableau Desktop / Tableau Public.
Connects to the churn dataset and pre-configures data sources and worksheets.
"""

from pathlib import Path
import xml.etree.ElementTree as ET


def generate_tableau_workbook(output_path: Path = None):
    project_root = Path(__file__).parent.parent
    if output_path is None:
        output_path = project_root / "tableau_churn_dashboard.twb"

    # CSV path relative to project
    csv_file = project_root / "outputs" / "query_1__overall_churn_rate.csv"

    twb_content = f"""<?xml me='1.0' encoding='utf-8' ?>
<workbook original-version='18.1' version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <preferences>
    <preference name='ui.encoding.shelf.height' value='24' />
    <preference name='ui.shelf.height' value='24' />
  </preferences>
  <datasources>
    <datasource caption='Telco Churn Clean Data' inline='true' name='federated.telco_churn' version='18.1'>
      <connection class='federated'>
        <named-connections>
          <named-connection caption='stg_customers' name='textscan.stg_customers'>
            <connection class='textscan' directory='{project_root / "outputs"}' filename='analysis_results.csv' password='' server='' />
          </named-connection>
        </named-connections>
      </connection>
      <column datatype='string' name='[customer_id]' role='dimension' type='nominal' />
      <column datatype='integer' name='[churn]' role='measure' type='quantitative' />
      <column datatype='integer' name='[tenure]' role='measure' type='quantitative' />
      <column datatype='real' name='[monthly_charges]' role='measure' type='quantitative' />
      <column datatype='real' name='[total_charges]' role='measure' type='quantitative' />
      <column datatype='string' name='[contract]' role='dimension' type='nominal' />
      <column datatype='string' name='[tenure_bucket]' role='dimension' type='ordinal' />
      <column datatype='string' name='[payment_method]' role='dimension' type='nominal' />
      <column datatype='string' name='[internet_service]' role='dimension' type='nominal' />
      <layout dim-ordering='alphabetic' dim-percentage='0.5' measure-ordering='alphabetic' measure-percentage='0.5' show-structure='true' />
    </datasource>
  </datasources>
  <worksheets>
    <worksheet name='Overall Churn KPI'>
      <table>
        <view>
          <datasources>
            <datasource caption='Telco Churn Clean Data' name='federated.telco_churn' />
          </datasources>
          <aggregation value='true' />
        </view>
        <style />
        <panes>
          <pane>
            <enum-record-attributes />
          </pane>
        </panes>
        <rows />
        <cols />
      </table>
    </worksheet>
    <worksheet name='Churn by Contract'>
      <table>
        <view>
          <datasources>
            <datasource caption='Telco Churn Clean Data' name='federated.telco_churn' />
          </datasources>
          <aggregation value='true' />
        </view>
        <style />
        <panes>
          <pane>
            <enum-record-attributes />
          </pane>
        </panes>
        <rows />
        <cols />
      </table>
    </worksheet>
    <worksheet name='Retention Curve'>
      <table>
        <view>
          <datasources>
            <datasource caption='Telco Churn Clean Data' name='federated.telco_churn' />
          </datasources>
          <aggregation value='true' />
        </view>
        <style />
        <panes>
          <pane>
            <enum-record-attributes />
          </pane>
        </panes>
        <rows />
        <cols />
      </table>
    </worksheet>
  </worksheets>
  <dashboards>
    <dashboard name='Telco Customer Churn Executive Dashboard'>
      <style />
      <size maxheight='900' maxwidth='1400' minheight='900' minwidth='1400' preset-index='0' type='fixed' />
      <zones>
        <zone h='100000' id='1' type='layout-basic' w='100000' x='0' y='0'>
          <zone h='98000' id='2' name='Overall Churn KPI' w='98000' x='1000' y='1000' />
        </zone>
      </zones>
    </dashboard>
  </dashboards>
  <windows>
    <window class='dashboard' name='Telco Customer Churn Executive Dashboard'>
      <active pane-specification='0' />
    </window>
  </windows>
</workbook>
"""

    output_path.write_text(twb_content, encoding="utf-8")
    print(f"[TABLEAU] Successfully generated Tableau Workbook file at: {output_path}")


if __name__ == "__main__":
    generate_tableau_workbook()
