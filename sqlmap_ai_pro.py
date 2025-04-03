#!/bin/env python3
# SQLMap AI Optimizer Pro v3.0 - Gelişmiş Otomatik Pentest Asistanı

import re
import sys
import json
import time
import random
import subprocess
from pathlib import Path
from datetime import datetime
import urllib.parse

class SQLMapProOptimizer:
    def __init__(self):
        self.error_db = self.load_error_patterns()
        self.proxy_list = self.load_proxies()
        self.tamper_scripts = self.detect_tampers()
        self.session_id = f"session_{int(time.time())}"
        
    def load_error_patterns(self):
        """Dinamik WAF pattern veritabanı"""
        return {
            '500': {
                'triggers': [r'500 \(Internal Server Error\)', r'SQL syntax error'],
                'solutions': {
                    'tampers': ['between', 'space2comment', 'space2mysqlblank'],
                    'params': ['--level=3', '--risk=2']
                },
                'learned': False
            },
            'cloudflare': {
                'triggers': [r'Cloudflare', r'403 Forbidden.*Ray ID'],
                'solutions': {
                    'tampers': ['randomcase', 'space2plus'],
                    'params': ['--delay=7', '--proxy={proxy}'],
                    'advanced': ['--flush-session', '--timeout=20']
                },
                'learned': True  # Cloudflare için öğrenilmiş pattern
            }
        }
    
    def load_proxies(self):
        """Proxy listesini dinamik yükleme"""
        try:
            with open('proxy_list.txt') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return ['http://127.0.0.1:8080']  # Varsayılan proxy
    
    def detect_tampers(self):
        """Sistemdeki tamper scriptlerini tespit et"""
        tampers = []
        try:
            tampers_path = Path('/usr/share/sqlmap/tamper/')
            if tampers_path.exists():
                tampers = [f.stem for f in tampers_path.glob('*.py') if not f.name.startswith('__')]
        except:
            pass
        return tampers or ['between', 'randomcase']  # Fallback
    
    def analyze_network(self, url):
        """Hedef sunucu özelliklerini analiz et"""
        parsed = urllib.parse.urlparse(url)
        return {
            'domain': parsed.netloc,
            'ports': self.scan_ports(parsed.netloc),
            'tech_stack': self.detect_tech(url)
        }
    
    def scan_ports(self, domain):
        """Temel port tarama (opsiyonel)"""
        common_ports = [80, 443, 8080, 8443]
        return common_ports  # Gerçekte nmap entegrasyonu yapılabilir
    
    def detect_tech(self, url):
        """WAF/Web sunucu tespiti"""
        try:
            result = subprocess.run(
                ['wafw00f', url],
                capture_output=True,
                text=True
            )
            return result.stdout
        except:
            return "Unknown"
    
    def adaptive_scan(self, url):
        """Akıllı tarama stratejisi"""
        print(f"\n🔍 [AI Phase] Hedef analizi başlatıldı: {url}")
        target_info = self.analyze_network(url)
        
        # Dinamik komut oluşturma
        base_cmd = [
            'sqlmap', '-u', url,
            '--batch',
            '--output-dir', f"./logs/{self.session_id}",
            '--csv', '--dump-format=JSON'
        ]
        
        # WAF'a göre ön ayar
        if 'cloudflare' in target_info['tech_stack'].lower():
            base_cmd.extend([
                '--tamper', ','.join(self.error_db['cloudflare']['solutions']['tampers']),
                '--delay', '5',
                '--proxy', random.choice(self.proxy_list)
            ])
        
        return base_cmd
    
    def realtime_analysis(self, process):
        """Gerçek zamanlı çıktı analizi"""
        optimization_history = []
        
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
            print(line.strip())  # Normal çıktıyı göster
            
            # Hata analizi
            for err_type, data in self.error_db.items():
                for pattern in data['triggers']:
                    if re.search(pattern, line, re.IGNORECASE):
                        if not data['learned']:
                            self.machine_learn(pattern)
                        
                        # Optimizasyon öner
                        solution = {
                            'type': err_type,
                            'timestamp': datetime.now().isoformat(),
                            'solution': data['solutions']
                        }
                        optimization_history.append(solution)
                        
                        yield solution
        
        # Tarama sonu raporu
        self.generate_report(optimization_history)
    
    def machine_learn(self, pattern):
        """Yeni pattern öğrenme"""
        print(f"\n🤖 [AI Learning] Yeni pattern öğreniliyor: {pattern[:50]}...")
        # Gerçekte burada ML modeli güncellenir
        self.error_db['custom'] = {
            'triggers': [pattern],
            'solutions': {
                'tampers': ['generic'],
                'params': ['--level=2']
            },
            'learned': True
        }
    
    def generate_report(self, optimizations):
        """PDF/HTML rapor oluştur"""
        report_file = f"./reports/{self.session_id}_report.html"
        with open(report_file, 'w') as f:
            f.write("<h1>SQLMap AI Optimizer Report</h1>")
            for opt in optimizations:
                f.write(f"<p><b>{opt['type']}</b>: {json.dumps(opt['solution'])}</p>")
        print(f"\n📄 Rapor oluşturuldu: {report_file}")
    
    def run(self, url):
        """Ana çalıştırıcı"""
        try:
            # 1. Akıllı ön tarama
            cmd = self.adaptive_scan(url)
            
            # 2. Prosesi başlat
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # 3. Gerçek zamanlı analiz
            for optimization in self.realtime_analysis(process):
                print(f"\n⚡ OPTIMIZE: {optimization['type']} detected!")
                print(f"   SOLUTION: {json.dumps(optimization['solution'], indent=2)}")
                
                # Otomatik optimize etme seçeneği
                if optimization['type'] == 'cloudflare':
                    choice = input("\n❓ WAF tespit edildi. Otomatik optimize edilsin mi? [Y/n]: ")
                    if choice.lower() != 'n':
                        new_params = [
                            '--tamper=randomcase,space2plus',
                            '--delay=7',
                            f'--proxy={random.choice(self.proxy_list)}'
                        ]
                        cmd.extend(new_params)
                        print(f"\n🔄 Yeni parametreler eklendi: {' '.join(new_params)}")
            
            # 4. Sonuç analizi
            print("\n✅ Tarama tamamlandı. Sonuçlar ./logs/ dizininde")
            
        except KeyboardInterrupt:
            print("\n⛔ Kullanıcı tarafından durduruldu!")
        except Exception as e:
            print(f"\n❌ Hata oluştu: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python3 sqlmap_ai_pro.py <target_url>")
        sys.exit(1)
    
    optimizer = SQLMapProOptimizer()
    optimizer.run(sys.argv[1])