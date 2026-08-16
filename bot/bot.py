# -*- coding: utf-8 -*-
import os, sys, traceback, logging, configparser
import xlsxwriter
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler

def main(argv):
    greetings()

    print('Press Crtl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    app = Flask(__name__)
    handler = RotatingFileHandler('bot.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    # REVIEW: Credenciais fixas no código-fonte são um problema de segurança.
    # Sugestão: Ler a URI do banco por variável de ambiente/secret manager e trocar está senha exposta.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123mudar@127.0.0.1:5432/bot_db'
    db = SQLAlchemy(app)
    config = configparser.ConfigParser()
    # REVIEW: Caminhos absolutos podem ser um problema; ConfigParser.read falha de forma silenciosa.
    # Sugestão: Monte o caminho relativo ao projeto e valide a existência do arquivo/diretório.
    config.read('/tmp/bot/settings/config.ini')

    var1 = int(config.get('scheduler','IntervalInMinutes'))
    app.logger.warning('Intervalo entre as execucoes do processo: {}'.format(var1))
    scheduler = BlockingScheduler()

    # REVIEW: A task1(db) está sendo executada imediatamente, em vez de agendada como callable.
    # Sugestão: Passar para uma função (callable) e args/kwargs.
    task1_instance = scheduler.add_job(task1(db), 'interval', id='task1_job', minutes=var1)

    try:
        scheduler.start()
    except(KeyboardInterrupt, SystemExit):
        pass

def greetings():
    print('             ##########################')
    print('             # - ACME - Tasks Robot - #')
    print('             # - v 1.0 - 2020-07-28 - #')
    print('             ##########################')

def task1(db):

    file_name = 'data_export_{0}.xlsx'.format(datetime.now().strftime("%Y%m%d%H%M%S"))
    file_path = os.path.join(os.path.curdir, file_name)
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()

    # REVIEW: SELECT * trás todas as informações e caso mudem o esquema da tabela podendo trazer falhas nas
    # informações previstas, também exportar dados sensíveis é perigoso.
    # Sugestão: Selecionar apenas colunas necessárias e sem conter o password se não for necessário.
    orders = db.session.execute('SELECT * FROM users;')
    
    index = 1
    
    worksheet.write('A{0}'.format(index),'Id')
    worksheet.write('B{0}'.format(index),'Name')
    worksheet.write('C{0}'.format(index),'Email')
    worksheet.write('D{0}'.format(index),'Password')
    worksheet.write('E{0}'.format(index),'Role Id')
    worksheet.write('F{0}'.format(index),'Created At')
    worksheet.write('G{0}'.format(index),'Updated At')
    
    for order in orders:
        index = index + 1

        print('Id: {0}'.format(order[0]))
        worksheet.write('A{0}'.format(index),order[0])
        print('Name: {0}'.format(order[1]))
        worksheet.write('B{0}'.format(index),order[1])
        print('Email: {0}'.format(order[2]))
        worksheet.write('C{0}'.format(index),order[2])
        # REVIEW: Informações sensíveis não devem ser utilizadas em logs.
        # Sugestão: Remova este print.
        print('Password: {0}'.format(order[3]))
        worksheet.write('D{0}'.format(index),order[3])
        print('Role Id: {0}'.format(order[4]))
        worksheet.write('E{0}'.format(index),order[4])
        print('Created At: {0}'.format(order[5]))
        worksheet.write('F{0}'.format(index),order[5])
        print('Updated At: {0}'.format(order[6]))
        worksheet.write('G{0}'.format(index),order[6])
        
    # REVIEW: A execução do workbook deve ser protegido com try/finally e limpeza da sessão.
    # Sugestão: Implemente um try/finally, além da limpeza de sessão.
    workbook.close()
    print('job executed!')

if __name__ == '__main__':
    main(sys.argv)
