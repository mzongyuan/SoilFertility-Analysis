import pandas as pd
import mysql.connector
from flask import request
from flask import Flask, render_template, jsonify, url_for
import numpy as np
import math

app = Flask(__name__)

#MySQL数据库
def mysql_init():
    connection = mysql.connector.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='Yanfa_1304',
        database='nature-analysis'
    )
    return connection

#读取Excel文件
def read_resource_file(file_path):
    data = pd.read_excel(file_path)
    return data

#保存文件至数据库
def save_data_to_database(connection, resourceData, batchNumber):
    cursor = connection.cursor()
    #循环处理
    for index, row in resourceData.iterrows():
        if index == 0:  # 跳过首行标题行
            continue
        batch_number = batchNumber
        sample_batch = row['样品号']
        sample_unit_weight = row['容重']
        sample_ph = row['pH']
        sample_organic = row['有机质']
        sample_total_nitrogen = row['全氮']
        sample_total_potassium = row['全钾']
        sample_total_phosphorus = row['全磷']
        sample_effective_phosphorus = row['有效磷']
        sample_quickacting_potassium = row['速效钾']
        sample_alkaline_nitrogen = row['碱解氮']
        # 插入数据到数据库表，如果主键（假设为sample_batch）存在冲突则进行更新
        query = "INSERT INTO sample_resource_data_t (batch_number,sample_batch, sample_unit_weight, sample_ph,sample_organic,sample_total_nitrogen,sample_total_potassium,sample_total_phosphorus,sample_effective_phosphorus,sample_quickacting_potassium,sample_alkaline_nitrogen) VALUES ('{}', '{}', '{}','{}', '{}', '{}','{}', '{}', '{}', '{}', '{}') ON DUPLICATE KEY UPDATE batch_number=VALUES(batch_number),sample_batch=VALUES(sample_batch),sample_unit_weight=VALUES(sample_unit_weight), sample_ph=VALUES(sample_ph), sample_organic=VALUES(sample_organic), sample_total_nitrogen=VALUES(sample_total_nitrogen), sample_total_potassium=VALUES(sample_total_potassium), sample_total_phosphorus=VALUES(sample_total_phosphorus), sample_effective_phosphorus=VALUES(sample_effective_phosphorus), sample_quickacting_potassium=VALUES(sample_quickacting_potassium), sample_alkaline_nitrogen=VALUES(sample_alkaline_nitrogen)".format(batch_number,sample_batch, sample_unit_weight, sample_ph,sample_organic,sample_total_nitrogen,sample_total_potassium,sample_total_phosphorus,sample_effective_phosphorus,sample_quickacting_potassium,sample_alkaline_nitrogen)
        cursor.execute(query)
    querybatch = "INSERT INTO sample_batch_data_t (batch_number, import_date, analysis_res) VALUES ('{}', NOW(), '{}')".format(batch_number, "未处理")
    cursor.execute(querybatch)
    connection.commit()
    cursor.close()
    pass


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data_batch_page')
def data_batch_page():
    return render_template('data_batch.html')

@app.route('/data_detail_page')
def data_detail_page():
    return render_template('data_detail.html')

@app.route('/process_data', methods=['POST'])
def process_data():
    batch_number = request.form['batchNumber']
    file = request.files['file_path']
    resource_data = read_resource_file(file)  # 读取本地文件数据
    connection = mysql_init()
    save_data_to_database(connection, resource_data, batch_number)
    return jsonify({"message": "Data processed successfully"})

@app.route('/query/resource', methods=['GET'])
def query_resource():
    batch_number = request.args.get('batchNumber')
    connection = mysql_init()
    cursor = connection.cursor()
    query = "SELECT * FROM sample_resource_data_t WHERE batch_number = %s"
    cursor.execute(query, (batch_number,))
    results = cursor.fetchall()
    cursor.close()
    # 将查询结果转换为期望的格式
    tableData = []
    for result in results:
        data_entry = {
            "batchNumber": result[0],
            "sampleBatch": result[1],
            "sampleUnitWeight": result[2],
            "samplePH": result[3],
            "sampleOrganic": result[4],
            "sampleTotalNitrogen": result[5],
            "sampleTotalPotassium": result[6],
            "sampleTotalPhosphorus": result[7],
            "sampleEffectivePhosphorus": result[8],
            "sampleQuickactingPotassium": result[9],
            "sampleAlkalineNitrogen": result[10]
}
        tableData.append(data_entry)
    return tableData

@app.route('/query/batch', methods=['GET'])
def query_batch():
    connection = mysql_init()
    cursor = connection.cursor()
    query = "SELECT * FROM sample_batch_data_t order by import_date asc"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    # 将查询结果转换为期望的格式
    tableData = []
    for result in results:
        data_entry = {
            "batchNumber": result[0],
            "importDate": result[1].strftime("%Y-%m-%d %H:%M:%S"),  # 格式化日期时间字段
            "analysisRes": result[2]
        }
        tableData.append(data_entry)
    return tableData

@app.route('/data/analysis', methods=['POST'])
def data_analysis():
    connection = mysql_init()
    cursor = connection.cursor()
    query = "SELECT * FROM sample_batch_data_t WHERE analysis_res = '未处理'"
    cursor.execute(query)
    batchResults = cursor.fetchall()
    # 循环未处理批次数据进行逻辑计算
    for batch in batchResults:
        batchNumber = batch[0]
        # 根据批次号查询源数据
        resquery = "SELECT * FROM sample_resource_data_t WHERE batch_number = %s"
        cursor.execute(resquery, (batchNumber,))
        resourceResults = cursor.fetchall()
        for resource in resourceResults:
            batchNumber = resource[0]
            sampleBatch = resource[1]
            sampleUnitWeight = resource[2]
            samplePH = resource[3]
            sampleOrganic = resource[4]
            sampleTotalNitrogen = resource[5]
            sampleTotalPotassium = resource[6]
            sampleTotalPhosphorus = resource[7]
            sampleEffectivePhosphorus = resource[8]
            sampleQuickactingPotassium = resource[9]
            sampleAlkalineNitrogen = resource[10]
            ## 分析计算
            #容重
            sampleUnitWeight_Xa = 1.45
            sampleUnitWeight_Xb = 1.35
            sampleUnitWeight_Xc = 1.25
            #PH
            samplePH_Xa = 9
            samplePH_Xb = 8
            samplePH_Xc = 7
            #有机质
            sampleOrganic_Xa = 10
            sampleOrganic_Xb = 20
            sampleOrganic_Xc = 30
            #全氮
            sampleTotalNitrogen_Xa = 0.75
            sampleTotalNitrogen_Xb = 1.5
            sampleTotalNitrogen_Xc = 2
            #全钾
            sampleTotalPotassium_Xa = 5
            sampleTotalPotassium_Xb = 20
            sampleTotalPotassium_Xc = 25
            #全磷
            sampleTotalPhosphorus_Xa = 0.4
            sampleTotalPhosphorus_Xb = 0.6
            sampleTotalPhosphorus_Xc = 1
            #有效磷
            sampleEffectivePhosphorus_Xa = 5
            sampleEffectivePhosphorus_Xb = 10
            sampleEffectivePhosphorus_Xc = 20
            #速效钾
            sampleQuickactingPotassium_Xa = 50
            sampleQuickactingPotassium_Xb = 100
            sampleQuickactingPotassium_Xc = 200
            #碱解氮
            sampleAlkalineNitrogen_Xa = 60
            sampleAlkalineNitrogen_Xb = 120
            sampleAlkalineNitrogen_Xc = 180
            # 计算分肥力系数
            Fi_sampleUnitWeight = calculateSpec(sampleUnitWeight, sampleUnitWeight_Xa, sampleUnitWeight_Xb, sampleUnitWeight_Xc)
            Fi_samplePH = calculateComm(samplePH, samplePH_Xa, samplePH_Xb, samplePH_Xc)
            Fi_sampleOrganic = calculateComm(sampleOrganic, sampleOrganic_Xa, sampleOrganic_Xb, sampleOrganic_Xc)
            Fi_sampleTotalNitrogen = calculateComm(sampleTotalNitrogen, sampleTotalNitrogen_Xa, sampleTotalNitrogen_Xb, sampleTotalNitrogen_Xc)
            Fi_sampleTotalPotassium = calculateComm(sampleTotalPotassium, sampleTotalPotassium_Xa, sampleTotalPotassium_Xb, sampleTotalPotassium_Xc)
            Fi_sampleTotalPhosphorus = calculateComm(sampleTotalPhosphorus, sampleTotalPhosphorus_Xa, sampleTotalPhosphorus_Xb, sampleTotalPhosphorus_Xc)
            Fi_sampleEffectivePhosphorus = calculateComm(sampleEffectivePhosphorus, sampleEffectivePhosphorus_Xa, sampleEffectivePhosphorus_Xb, sampleEffectivePhosphorus_Xc)
            Fi_sampleQuickactingPotassium = calculateComm(sampleQuickactingPotassium, sampleQuickactingPotassium_Xa, sampleQuickactingPotassium_Xb, sampleQuickactingPotassium_Xc)
            Fi_sampleAlkalineNitrogen = calculateComm(sampleAlkalineNitrogen, sampleAlkalineNitrogen_Xa, sampleAlkalineNitrogen_Xb, sampleAlkalineNitrogen_Xc)
            # 计算平均值
            Fi_values = [Fi_sampleUnitWeight, Fi_samplePH, Fi_sampleOrganic, Fi_sampleTotalNitrogen, Fi_sampleTotalPotassium, Fi_sampleTotalPhosphorus, Fi_sampleEffectivePhosphorus, Fi_sampleQuickactingPotassium, Fi_sampleAlkalineNitrogen]
            Fi_avg = np.mean(Fi_values)
            Fi_min = np.min(Fi_values)

            ## 内梅罗综合指数算法计算肥力系数
            F = math.sqrt((Fi_avg*Fi_avg + Fi_min*Fi_min) / 2) * ((9 - 1) / 9)
            ## 评价结果
            sampleResult = ''
            print("样品:", sampleBatch)
            if F >= 2.5:
                print("很肥沃:", F)
                sampleResult = "很肥沃"
            elif F < 2.5 and F >= 1.7:
                print("肥沃:", F)
                sampleResult = "肥沃"
            elif F < 1.7 and F >= 0.8:
                print("一般:", F)
                sampleResult = "一般"
            else:
                print("贫瘠:", F)
                sampleResult = "贫瘠"
            ## 保存到数据库
            # 插入数据到数据库表，如果主键（假设为sample_batch）存在冲突则进行更新
            saveQuery = "INSERT INTO sample_result_data_t (batch_number, sample_batch, sample_unit_weight, sample_ph, sample_organic, sample_total_nitrogen, sample_total_potassium, sample_total_phosphorus, sample_effective_phosphorus, sample_quickacting_potassium, sample_alkaline_nitrogen, sample_fi, sample_result) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE sample_batch=VALUES(sample_batch), sample_unit_weight=VALUES(sample_unit_weight), sample_ph=VALUES(sample_ph), sample_organic=VALUES(sample_organic), sample_total_nitrogen=VALUES(sample_total_nitrogen), sample_total_potassium=VALUES(sample_total_potassium), sample_total_phosphorus=VALUES(sample_total_phosphorus), sample_effective_phosphorus=VALUES(sample_effective_phosphorus), sample_quickacting_potassium=VALUES(sample_quickacting_potassium), sample_alkaline_nitrogen=VALUES(sample_alkaline_nitrogen), sample_fi=VALUES(sample_fi), sample_result=VALUES(sample_result)"
            cursor.execute(saveQuery, (batchNumber, sampleBatch, sampleUnitWeight, samplePH, sampleOrganic, sampleTotalNitrogen, sampleTotalPotassium, sampleTotalPhosphorus, sampleEffectivePhosphorus, sampleQuickactingPotassium, sampleAlkalineNitrogen, F, sampleResult))
        ## 更新批次处理结果
        updateQuery = "UPDATE sample_batch_data_t SET analysis_res='已处理' WHERE batch_number=%s"
        cursor.execute(updateQuery, (batchNumber,))
    connection.commit()
    cursor.close()

    return jsonify({"message": "Data analysis successfully"})

@app.route('/data/export', methods=['POST'])
def data_export():
    connection = mysql_init()
    cursor = connection.cursor()
    query = "SELECT * FROM sample_result_data_t"
    cursor.execute(query)
    results = cursor.fetchall()
    # 将查询结果转换为DataFrame
    df = pd.DataFrame(results, columns=[col[0] for col in cursor.description])
    # 保存DataFrame到Excel文件
    file_path = r'D:\AnalysisResult.xlsx'
    df.to_excel(file_path, index=False)
    connection.commit()
    cursor.close()

    return jsonify({"message": "Data Export successfully"})

## 容重肥力系数
def calculateSpec(Ci, Xa, Xb, Xc):
    if Ci >= Xa:
        return 1.45/Ci
    elif Ci <= Xb and Ci < Xa:
        return 1 + (Ci - Xa) / (Xb - Xa)
    elif Ci >= Xc and Ci < Xb:
        return 2 + (Ci - Xb) / (Xc - Xb)
    else:
        return 3
    pass

## 其他项肥力系数
def calculateComm(Ci, Xa, Xb, Xc):
    if Ci <= Xa:
        return Ci/Xa
    elif Ci > Xa and Ci <= Xb:
        return 1 + (Ci - Xa) / (Xb - Xa)
    elif Ci > Xb and Ci <= Xc:
        return 2 + (Ci - Xb) / (Xc - Xb)
    else:
        return 3
    pass

if __name__ == '__main__':
    app.run(debug=True)