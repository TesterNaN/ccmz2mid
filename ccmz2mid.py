#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ccmz2mid - 虫虫钢琴ccmz文件转midi工具
Copyright (C) 2025 TesterNaN

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


import json
import os
import zipfile
import tempfile
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from collections import defaultdict
from typing import Dict, List, Tuple

try:
    import mido
    from mido import MidiFile, MidiTrack, Message, MetaMessage
    MIDO_AVAILABLE = True
except ImportError:
    MIDO_AVAILABLE = False
    print("⚠️ 警告: mido 库未安装，将无法转换为 MIDI 格式")
    print("请运行: pip install mido")


def print_header():    
    print("=" * 60)
    print("🎵 CCMZ 到 MIDI 转换工具")
    print("=" * 60)


def print_menu():    
    print("\n请选择操作:")
    print("1. 从 URL 下载并转换 CCMZ 文件")
    print("2. 转换本地 CCMZ 文件")
    print("3. 使用示例 URL 测试")
    print("4. 退出")
    print("-" * 40)


def get_input(prompt, default="", required=True):
    
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input and required:
            print("❌ 请输入有效值！")
            continue
        
        return user_input


class CcmzDownloader:    
    @staticmethod
    def download_ccmz(url: str, output_path: str = None) -> str:

        if output_path is None:
            # 从 URL 提取文件名
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename:
                filename = "downloaded.ccmz"
            output_path = filename
        
        print(f"📥 正在从 {url} 下载 CCMZ 文件...")
        
        # 设置 User-Agent 避免被拒绝
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        request = Request(url, headers=headers)
        
        try:
            with urlopen(request) as response:
                # 检查响应状态
                if response.status != 200:
                    raise Exception(f"下载失败，HTTP 状态码: {response.status}")
                
                # 读取数据
                data = response.read()
                
                # 保存文件
                with open(output_path, 'wb') as f:
                    f.write(data)
                
                file_size = len(data)
                print(f"✅ 下载完成: {output_path} ({file_size:,} 字节)")
                return output_path
                
        except Exception as e:
            raise Exception(f"下载失败: {str(e)}")


class CcmzExtractor:    
    @staticmethod
    def extract_ccmz(ccmz_path: str, output_dir: str = None) -> str:
        if not os.path.exists(ccmz_path):
            raise FileNotFoundError(f"CCMZ 文件不存在: {ccmz_path}")
        
        # 创建输出目录
        if output_dir is None:
            output_dir = os.path.splitext(ccmz_path)[0] + "_extracted"
        
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"🔍 正在提取 CCMZ 文件: {ccmz_path}")
        
        # 读取 CCMZ 文件
        with open(ccmz_path, 'rb') as f:
            data = f.read()
        
        file_size = len(data)
        print(f"📄 文件大小: {file_size:,} 字节")
        
        # 第一个字节是版本号
        version = data[0]
        print(f"📊 CCMZ 版本: {version}")
        
        # 剩余数据
        remaining = data[1:]
        
        # 根据版本解密
        if version == 1:
            # 版本1: 直接就是ZIP
            decrypted = remaining
            print("🔓 使用版本1解密（直接ZIP）")
        elif version == 2:
            # 版本2: 每个字节奇偶性转换
            print("🔓 使用版本2解密（奇偶转换）...")
            decrypted = bytearray()
            for i, byte in enumerate(remaining):
                if byte % 2 == 0:  # 偶数
                    decrypted.append(byte + 1)
                else:  # 奇数
                    decrypted.append(byte - 1)
                
                # 显示进度
                if i % 100000 == 0 and i > 0:
                    progress = i / len(remaining) * 100
                    print(f"  解密进度: {progress:.1f}%")
            
            decrypted = bytes(decrypted)
            print("✅ 解密完成")
        else:
            raise ValueError(f"❌ 不支持的 CCMZ 版本: {version}")
        
        # 保存解密后的 ZIP 文件
        zip_path = os.path.join(output_dir, "decrypted.zip")
        with open(zip_path, 'wb') as f:
            f.write(decrypted)
        
        print(f"💾 已保存解密文件: {zip_path}")
        
        # 提取 ZIP 文件
        json_path = None
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                files = zf.namelist()
                print(f"📦 ZIP 包含 {len(files)} 个文件:")
                
                # 查找 midi.json 文件
                for filename in files:
                    info = zf.getinfo(filename)
                    file_size_str = f"{info.file_size:,} 字节"
                    print(f"  📁 {filename} ({file_size_str})")
                    
                    # 解压文件
                    output_path = os.path.join(output_dir, filename)
                    zf.extract(filename, output_dir)
                    
                    # 检查是否为 midi.json
                    if filename.lower() == 'midi.json':
                        json_path = output_path
                        print(f"🎯 找到 JSON 文件: {json_path}")
        
        except zipfile.BadZipFile:
            raise ValueError("⚠️ 解密后的文件不是有效的 ZIP 格式")

        if json_path is None:
            raise FileNotFoundError("❌ 在 CCMZ 文件中未找到 JSON 数据")
        
        return json_path


class MidiJsonToMidoConverter:    
    def __init__(self, json_path: str, output_path: str = None):
        self.json_path = json_path
        self.output_path = output_path or json_path.replace('.json', '.mid')
        
        print(f"📖 正在加载 JSON 文件: {json_path}")
        # 加载 JSON 数据
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        # MIDI 常量
        self.TICKS_PER_BEAT = 480  # 四分音符的ticks数
        self.DEFAULT_TEMPO = 625000  # 微秒/四分音符
        
        # 创建 MIDI 文件
        self.mid = MidiFile(ticks_per_beat=self.TICKS_PER_BEAT)
        
        # 分析数据结构
        self._analyze_data()
    
    def _analyze_data(self):        
        print("📊 分析数据结构...")
        
        # 统计信息
        events = self.data.get('events', [])
        tracks = self.data.get('tracks', [])
        measures = self.data.get('measures', {})
        tempos = self.data.get('tempos', [])
        beat_infos = self.data.get('beatInfos', [])
        
        print(f"  事件数量: {len(events):,}")
        print(f"  轨道数量: {len(tracks)}")
        print(f"  小节数量: {len(measures)}")
        print(f"  速度变化: {len(tempos)} 处")
        print(f"  拍号变化: {len(beat_infos)} 处")
        
        # 统计音符事件
        note_events = 0
        for event in events:
            event_data = event.get('event', [])
            if event_data and event_data[0] & 0xF0 in [0x80, 0x90]:  # Note On/Off
                note_events += 1
        
        print(f"  音符事件: {note_events:,}")
    
    def get_format_type(self) -> int:        
        # 根据轨道数判断格式
        if len(self.data.get('tracks', [])) > 1:
            return 1  # 多轨道同步
        else:
            return 0  # 单轨道
    
    def create_tempo_map(self) -> List[Tuple[int, int]]:
        tempos = self.data.get('tempos', [])
        tempo_map = []
        
        for tempo_info in tempos:
            tick = tempo_info.get('tick', 0)
            tempo = tempo_info.get('tempo', self.DEFAULT_TEMPO)
            tempo_map.append((tick, tempo))
        
        # 如果没有速度事件，添加默认速度
        if not tempo_map:
            tempo_map.append((0, self.DEFAULT_TEMPO))
        
        print(f"🎵 速度映射: {len(tempo_map)} 个速度点")
        return tempo_map
    
    def create_time_signature_map(self) -> List[Tuple[int, int, int]]:
        beat_infos = self.data.get('beatInfos', [])
        time_sig_map = []
        
        for beat_info in beat_infos:
            tick = beat_info.get('tick', 0)
            numerator = beat_info.get('beats', 4)
            denominator = beat_info.get('beatsUnit', 4)
            time_sig_map.append((tick, numerator, denominator))
        
        print(f"🎼 拍号映射: {len(time_sig_map)} 个拍号点")
        return time_sig_map
    
    def group_events_by_track(self) -> Dict[int, List[Dict]]:
        events = self.data.get('events', [])
        track_events = defaultdict(list)
        
        for event in events:
            track = event.get('track', 0)
            track_events[track].append(event)
        
        # 按 tick 排序每个轨道的事件
        for track in track_events:
            track_events[track].sort(key=lambda x: x.get('tick', 0))
        
        print(f"📁 事件分组: {len(track_events)} 个轨道")
        return dict(track_events)
    
    def create_meta_track(self) -> MidiTrack:
        track = MidiTrack()
        
        # 设置文件格式
        self.mid.type = self.get_format_type()
        
        # 添加速度事件
        tempo_map = self.create_tempo_map()
        last_tick = 0
        
        for tick, tempo in tempo_map:
            delta = tick - last_tick
            track.append(MetaMessage('set_tempo', tempo=tempo, time=delta))
            last_tick = tick
        
        # 添加拍号事件
        time_sig_map = self.create_time_signature_map()
        last_tick = 0
        
        for tick, numerator, denominator in time_sig_map:
            delta = tick - last_tick
            # 转换分母为2的幂次
            denominator_power = 2  # 默认4/4拍
            if denominator == 2:
                denominator_power = 1
            elif denominator == 8:
                denominator_power = 3
            elif denominator == 16:
                denominator_power = 4
            
            track.append(MetaMessage('time_signature', 
                                    numerator=numerator, 
                                    denominator=denominator_power, 
                                    time=delta))
            last_tick = tick
        
        # 添加轨道结束事件
        track.append(MetaMessage('end_of_track', time=0))
        
        print(f"📝 元数据轨道创建完成: {len(track)} 个事件")
        return track
    
    def parse_midi_message(self, event_data: List[int]) -> Message:
        if not event_data:
            return None
        
        status = event_data[0]
        
        # 检查是否为 MIDI 状态字节
        if status < 0x80:
            return None
        
        # 获取消息类型和通道
        msg_type = status & 0xF0
        channel = status & 0x0F
        
        # 根据消息类型创建 Message 对象
        if msg_type == 0x80:  # Note Off
            if len(event_data) >= 3:
                return Message('note_off', 
                              channel=channel, 
                              note=event_data[1], 
                              velocity=event_data[2], 
                              time=0)
        elif msg_type == 0x90:  # Note On
            if len(event_data) >= 3:
                # 力度为0的Note On视为Note Off
                if event_data[2] == 0:
                    return Message('note_off', 
                                  channel=channel, 
                                  note=event_data[1], 
                                  velocity=0, 
                                  time=0)
                else:
                    return Message('note_on', 
                                  channel=channel, 
                                  note=event_data[1], 
                                  velocity=event_data[2], 
                                  time=0)
        elif msg_type == 0xA0:  # Aftertouch
            if len(event_data) >= 3:
                return Message('polytouch', 
                              channel=channel, 
                              note=event_data[1], 
                              value=event_data[2], 
                              time=0)
        elif msg_type == 0xB0:  # Control Change
            if len(event_data) >= 3:
                return Message('control_change', 
                              channel=channel, 
                              control=event_data[1], 
                              value=event_data[2], 
                              time=0)
        elif msg_type == 0xC0:  # Program Change
            if len(event_data) >= 2:
                return Message('program_change', 
                              channel=channel, 
                              program=event_data[1], 
                              time=0)
        elif msg_type == 0xD0:  # Channel Pressure
            if len(event_data) >= 2:
                return Message('aftertouch', 
                              channel=channel, 
                              value=event_data[1], 
                              time=0)
        elif msg_type == 0xE0:  # Pitch Bend
            if len(event_data) >= 3:
                # 合并两个7位值为14位值
                value = (event_data[2] << 7) | event_data[1]
                return Message('pitchwheel', 
                              channel=channel, 
                              pitch=value - 8192,  # mido使用-8192到8191
                              time=0)
        
        return None
    
    def create_music_track(self, track_index: int, track_events: List[Dict], 
                          tracks_data: List[Dict]) -> MidiTrack:
        track = MidiTrack()
        
        # 添加轨道名称
        track_name = f"Track {track_index}"
        track.append(MetaMessage('track_name', name=track_name, time=0))
        
        # 获取轨道音色信息
        if track_index < len(tracks_data):
            track_info = tracks_data[track_index]
            program = track_info.get('program', 0)
            channel = track_info.get('channel', track_index % 16)
            
            # 添加音色变更事件
            if program >= 0:
                track.append(Message('program_change', 
                                    channel=channel, 
                                    program=program, 
                                    time=0))
        
        # 处理事件，计算 delta time
        last_tick = 0
        processed_events = 0
        
        for event in track_events:
            tick = event.get('tick', 0)
            delta = tick - last_tick
            
            # 解析 MIDI 消息
            event_data = event.get('event', [])
            if event_data:
                msg = self.parse_midi_message(event_data)
                if msg:
                    # 设置 delta time
                    msg.time = delta
                    track.append(msg)
                    processed_events += 1
            
            last_tick = tick
        
        # 添加轨道结束事件
        track.append(MetaMessage('end_of_track', time=0))
        
        print(f"  轨道 {track_index}: {len(track_events)} 个事件 -> {processed_events} 个MIDI事件")
        return track
    
    def convert(self) -> MidiFile:
        print("🔄 开始转换 JSON 到 MIDI...")
        
        # 1. 添加元数据轨道
        meta_track = self.create_meta_track()
        self.mid.tracks.append(meta_track)
        
        # 2. 按轨道分组事件
        track_events_dict = self.group_events_by_track()
        tracks_data = self.data.get('tracks', [])
        
        # 3. 为每个轨道创建音乐轨道
        for track_index in range(len(tracks_data)):
            events = track_events_dict.get(track_index, [])
            track = self.create_music_track(track_index, events, tracks_data)
            self.mid.tracks.append(track)
        
        # 4. 如果没有轨道数据但有事件，创建默认轨道
        if not tracks_data and track_events_dict:
            for track_index, events in track_events_dict.items():
                track = self.create_music_track(track_index, events, [])
                self.mid.tracks.append(track)
        
        total_tracks = len(self.mid.tracks)
        total_events = sum(len(track) for track in self.mid.tracks)
        print(f"✅ 转换完成: {total_tracks} 个轨道，{total_events} 个MIDI事件")
        
        return self.mid
    
    def save(self, output_path: str = None):
        if output_path:
            self.output_path = output_path
        
        # 执行转换
        midi_file = self.convert()
        
        # 保存文件
        midi_file.save(self.output_path)
        
        # 显示MIDI文件信息
        print(f"💾 MIDI 文件已保存: {self.output_path}")
        print(f"  文件格式: {midi_file.type}")
        print(f"  时间精度: {midi_file.ticks_per_beat} ticks/beat")
        print(f"  轨道数量: {len(midi_file.tracks)}")
        print(f"  总时长: {midi_file.length:.2f} 秒")
        
        return midi_file


def process_ccmz_file(ccmz_path, output_midi_path, keep_temp=False):
    print(f"\n🔧 开始处理 CCMZ 文件: {ccmz_path}")
    
    # 创建临时工作目录
    work_dir = tempfile.mkdtemp(prefix="ccmz_to_midi_")
    print(f"📁 临时工作目录: {work_dir}")
    
    try:
        # 步骤1: 提取 JSON 数据
        print("\n📂 步骤1: 提取 CCMZ 文件...")
        json_path = CcmzExtractor.extract_ccmz(ccmz_path, work_dir)
        
        if not MIDO_AVAILABLE:
            print("❌ 错误: mido 库未安装，无法转换为 MIDI 格式")
            print("请运行: pip install mido")
            return False
        
        # 步骤2: 转换为 MIDI
        print("\n🎵 步骤2: 转换为 MIDI 格式...")
        converter = MidiJsonToMidoConverter(json_path, output_midi_path)
        converter.save()
        
        # 清理临时文件
        if not keep_temp:
            import shutil
            shutil.rmtree(work_dir)
            print(f"🗑️  已清理临时目录: {work_dir}")
        else:
            print(f"📁 临时文件保留在: {work_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")
        return False


def download_and_convert():
    print("\n🌐 从 URL 下载并转换")
    print("-" * 40)
    
    # 获取 URL
    example_url = "https://s201.lzjoy.com/res/statics/fileupload/ccmz/202601/11/1145982-20260103221636695924c41c86a.ccmz"
    
    print(f"示例 URL: {example_url}")
    url = get_input("请输入 CCMZ 文件 URL", default="")
    
    if not url:
        print("❌ 未输入 URL，使用示例 URL")
        url = example_url
    
    # 获取输出文件名
    output_file = get_input("请输入输出 MIDI 文件名", default="output.mid")
    
    # 是否保留临时文件
    keep_temp_input = get_input("是否保留临时文件? (y/n)", default="n", required=False)
    keep_temp = keep_temp_input.lower() == 'y'
    
    try:
        print(f"\n🚀 开始处理 URL: {url}")
        
        # 下载文件
        downloaded_file = CcmzDownloader.download_ccmz(url)
        
        # 处理文件
        success = process_ccmz_file(downloaded_file, output_file, keep_temp)
        
        if success:
            print(f"\n🎉 转换完成！MIDI 文件已保存为: {output_file}")
        else:
            print("❌ 转换失败")
            
    except Exception as e:
        print(f"❌ 处理失败: {str(e)}")


def convert_local_file():
    print("\n💾 转换本地 CCMZ 文件")
    print("-" * 40)
    
    # 获取本地文件路径
    file_path = get_input("请输入 CCMZ 文件路径", default="")
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 获取输出文件名
    default_name = os.path.splitext(os.path.basename(file_path))[0] + ".mid"
    output_file = get_input("请输入输出 MIDI 文件名", default=default_name)
    
    # 是否保留临时文件
    keep_temp_input = get_input("是否保留临时文件? (y/n)", default="n", required=False)
    keep_temp = keep_temp_input.lower() == 'y'
    
    # 处理文件
    success = process_ccmz_file(file_path, output_file, keep_temp)
    
    if success:
        print(f"\n🎉 转换完成！MIDI 文件已保存为: {output_file}")
    else:
        print("❌ 转换失败")


def use_example_url():
    print("\n🧪 使用示例 URL 测试")
    print("-" * 40)
    
    example_url = "https://s201.lzjoy.com/res/statics/fileupload/ccmz/202601/11/1145982-20260103221636695924c41c86a.ccmz"
    print(f"示例 URL: {example_url}")
    
    output_file = get_input("请输入输出 MIDI 文件名", default="example_output.mid")
    
    # 是否保留临时文件
    keep_temp_input = get_input("是否保留临时文件? (y/n)", default="n", required=False)
    keep_temp = keep_temp_input.lower() == 'y'
    
    try:
        print(f"\n🚀 开始处理示例 URL...")
        
        # 下载文件
        downloaded_file = CcmzDownloader.download_ccmz(example_url, "example.ccmz")
        
        # 处理文件
        success = process_ccmz_file(downloaded_file, output_file, keep_temp)
        
        if success:
            print(f"\n🎉 测试完成！MIDI 文件已保存为: {output_file}")
        else:
            print("❌ 测试失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")


def check_dependencies():
    print("🔍 检查依赖库...")
    
    missing_libs = []
    
    if not MIDO_AVAILABLE:
        missing_libs.append("mido")
    
    if missing_libs:
        print(f"❌ 缺少以下库: {', '.join(missing_libs)}")
        print("请运行以下命令安装:")
        for lib in missing_libs:
            print(f"  pip install {lib}")
        
        choice = input("\n是否现在安装? (y/n): ").lower()
        if choice == 'y':
            import subprocess
            import sys
            
            for lib in missing_libs:
                print(f"正在安装 {lib}...")
                try:
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])
                    print(f"✅ {lib} 安装成功")
                except Exception as e:
                    print(f"❌ 安装 {lib} 失败: {str(e)}")
            
            # 重新导入检查
            print("\n🔍 重新检查依赖...")
            return check_dependencies()
        else:
            print("⚠️ 继续运行，但部分功能可能无法使用")
            return False
    
    print("✅ 所有依赖库已安装")
    return True


def main():
    print_header()
    
    # 检查依赖
    if not check_dependencies():
        print("\n⚠️ 继续运行可能会有功能限制")
    
    while True:
        print_menu()
        
        choice = input("请选择 (1-4): ").strip()
        
        if choice == "1":
            download_and_convert()
        elif choice == "2":
            convert_local_file()
        elif choice == "3":
            use_example_url()
        elif choice == "4":
            print("\n👋 感谢使用，再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        # 询问是否继续
        if choice != "4":
            continue_choice = input("\n是否继续使用其他功能? (y/n): ").lower()
            if continue_choice != 'y':
                print("\n👋 感谢使用，再见！")
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 程序出错: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
