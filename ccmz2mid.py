#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ccmz2mid - 虫虫钢琴ccmz文件转midi工具
Copyright (C) 2026 TesterNaN

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


def print_header():    
    print("CCMZ 到 MIDI 转换工具")


def print_menu():    
    print("\n请选择操作:")
    print("1. 从 URL 下载并转换 CCMZ 文件")
    print("2. 转换本地 CCMZ 文件")
    print("3. 退出")


def get_input(prompt, default="", required=True):
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input and required:
            print("请输入有效值！")
            continue
        
        return user_input


class CcmzDownloader:    
    @staticmethod
    def download_ccmz(url: str) -> str:
        temp_dir = tempfile.mkdtemp(prefix="ccmz_download_")
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = "downloaded.ccmz"
        output_path = os.path.join(temp_dir, filename)
        
        print("下载中...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        request = Request(url, headers=headers)
        
        try:
            with urlopen(request) as response:
                if response.status != 200:
                    raise Exception(f"下载失败，HTTP 状态码: {response.status}")
                
                data = response.read()
                
                with open(output_path, 'wb') as f:
                    f.write(data)
                
                return output_path
                
        except Exception as e:
            raise Exception(f"下载失败: {str(e)}")


class CcmzExtractor:    
    @staticmethod
    def extract_ccmz(ccmz_path: str, output_dir: str = None) -> str:
        if not os.path.exists(ccmz_path):
            raise FileNotFoundError(f"CCMZ 文件不存在: {ccmz_path}")
        
        if output_dir is None:
            output_dir = os.path.splitext(ccmz_path)[0] + "_extracted"
        
        os.makedirs(output_dir, exist_ok=True)
        
        with open(ccmz_path, 'rb') as f:
            data = f.read()
        
        version = data[0]
        remaining = data[1:]
        
        if version == 1:
            decrypted = remaining
        elif version == 2:
            decrypted = bytearray()
            for byte in remaining:
                if byte % 2 == 0:
                    decrypted.append(byte + 1)
                else:
                    decrypted.append(byte - 1)
            decrypted = bytes(decrypted)
        else:
            raise ValueError(f"不支持的 CCMZ 版本: {version}")
        
        zip_path = os.path.join(output_dir, "decrypted.zip")
        with open(zip_path, 'wb') as f:
            f.write(decrypted)
        
        json_path = None
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for filename in zf.namelist():
                    output_path = os.path.join(output_dir, filename)
                    zf.extract(filename, output_dir)
                    
                    if filename.lower() == 'midi.json':
                        json_path = output_path
        
        except zipfile.BadZipFile:
            raise ValueError("解密后的文件不是有效的 ZIP 格式")

        if json_path is None:
            raise FileNotFoundError("在 CCMZ 文件中未找到 JSON 数据")
        
        return json_path


class MidiJsonToMidoConverter:    
    def __init__(self, json_path: str, output_path: str = None):
        self.json_path = json_path
        self.output_path = output_path or json_path.replace('.json', '.mid')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.TICKS_PER_BEAT = 480
        self.DEFAULT_TEMPO = 625000
        
        self.mid = MidiFile(ticks_per_beat=self.TICKS_PER_BEAT)
    
    def get_format_type(self) -> int:        
        if len(self.data.get('tracks', [])) > 1:
            return 1
        else:
            return 0
    
    def create_tempo_map(self) -> List[Tuple[int, int]]:
        tempos = self.data.get('tempos', [])
        tempo_map = []
        
        for tempo_info in tempos:
            tick = tempo_info.get('tick', 0)
            tempo = tempo_info.get('tempo', self.DEFAULT_TEMPO)
            tempo_map.append((tick, tempo))
        
        if not tempo_map:
            tempo_map.append((0, self.DEFAULT_TEMPO))
        
        return tempo_map
    
    def create_time_signature_map(self) -> List[Tuple[int, int, int]]:
        beat_infos = self.data.get('beatInfos', [])
        time_sig_map = []
        
        for beat_info in beat_infos:
            tick = beat_info.get('tick', 0)
            numerator = beat_info.get('beats', 4)
            denominator = beat_info.get('beatsUnit', 4)
            time_sig_map.append((tick, numerator, denominator))
        
        return time_sig_map
    
    def group_events_by_track(self) -> Dict[int, List[Dict]]:
        events = self.data.get('events', [])
        track_events = defaultdict(list)
        
        for event in events:
            track = event.get('track', 0)
            track_events[track].append(event)
        
        for track in track_events:
            track_events[track].sort(key=lambda x: x.get('tick', 0))
        
        return dict(track_events)
    
    def create_meta_track(self) -> MidiTrack:
        track = MidiTrack()
        
        self.mid.type = self.get_format_type()
        
        tempo_map = self.create_tempo_map()
        last_tick = 0
        
        for tick, tempo in tempo_map:
            delta = tick - last_tick
            track.append(MetaMessage('set_tempo', tempo=tempo, time=delta))
            last_tick = tick
        
        time_sig_map = self.create_time_signature_map()
        last_tick = 0
        
        for tick, numerator, denominator in time_sig_map:
            delta = tick - last_tick
            denominator_power = 2
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
        
        track.append(MetaMessage('end_of_track', time=0))
        
        return track
    
    def parse_midi_message(self, event_data: List[int]) -> Message:
        if not event_data:
            return None
        
        status = event_data[0]
        
        if status < 0x80:
            return None
        
        msg_type = status & 0xF0
        channel = status & 0x0F
        
        if msg_type == 0x80:
            if len(event_data) >= 3:
                return Message('note_off', 
                              channel=channel, 
                              note=event_data[1], 
                              velocity=event_data[2], 
                              time=0)
        elif msg_type == 0x90:
            if len(event_data) >= 3:
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
        elif msg_type == 0xA0:
            if len(event_data) >= 3:
                return Message('polytouch', 
                              channel=channel, 
                              note=event_data[1], 
                              value=event_data[2], 
                              time=0)
        elif msg_type == 0xB0:
            if len(event_data) >= 3:
                return Message('control_change', 
                              channel=channel, 
                              control=event_data[1], 
                              value=event_data[2], 
                              time=0)
        elif msg_type == 0xC0:
            if len(event_data) >= 2:
                return Message('program_change', 
                              channel=channel, 
                              program=event_data[1], 
                              time=0)
        elif msg_type == 0xD0:
            if len(event_data) >= 2:
                return Message('aftertouch', 
                              channel=channel, 
                              value=event_data[1], 
                              time=0)
        elif msg_type == 0xE0:
            if len(event_data) >= 3:
                value = (event_data[2] << 7) | event_data[1]
                return Message('pitchwheel', 
                              channel=channel, 
                              pitch=value - 8192,
                              time=0)
        
        return None
    
    def create_music_track(self, track_index: int, track_events: List[Dict], 
                          tracks_data: List[Dict]) -> MidiTrack:
        track = MidiTrack()
        
        track_name = f"Track {track_index}"
        track.append(MetaMessage('track_name', name=track_name, time=0))
        
        if track_index < len(tracks_data):
            track_info = tracks_data[track_index]
            program = track_info.get('program', 0)
            channel = track_info.get('channel', track_index % 16)
            
            if program >= 0:
                track.append(Message('program_change', 
                                    channel=channel, 
                                    program=program, 
                                    time=0))
        
        last_tick = 0
        processed_events = 0
        
        for event in track_events:
            tick = event.get('tick', 0)
            delta = tick - last_tick
            
            event_data = event.get('event', [])
            if event_data:
                msg = self.parse_midi_message(event_data)
                if msg:
                    msg.time = delta
                    track.append(msg)
                    processed_events += 1
            
            last_tick = tick
        
        track.append(MetaMessage('end_of_track', time=0))
        
        return track
    
    def convert(self) -> MidiFile:
        meta_track = self.create_meta_track()
        self.mid.tracks.append(meta_track)
        
        track_events_dict = self.group_events_by_track()
        tracks_data = self.data.get('tracks', [])
        
        for track_index in range(len(tracks_data)):
            events = track_events_dict.get(track_index, [])
            track = self.create_music_track(track_index, events, tracks_data)
            self.mid.tracks.append(track)
        
        if not tracks_data and track_events_dict:
            for track_index, events in track_events_dict.items():
                track = self.create_music_track(track_index, events, [])
                self.mid.tracks.append(track)
        
        return self.mid
    
    def save(self, output_path: str = None):
        if output_path:
            self.output_path = output_path
        
        midi_file = self.convert()
        midi_file.save(self.output_path)
        
        return midi_file


def process_ccmz_file(ccmz_path, output_midi_path):
    work_dir = tempfile.mkdtemp(prefix="ccmz_to_midi_")
    
    try:
        json_path = CcmzExtractor.extract_ccmz(ccmz_path, work_dir)
        
        if not MIDO_AVAILABLE:
            print("错误: mido 库未安装，无法转换为 MIDI 格式")
            print("请运行: pip install mido")
            return False
        
        converter = MidiJsonToMidoConverter(json_path, output_midi_path)
        converter.save()
        
        import shutil
        shutil.rmtree(work_dir)
        
        return True
        
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return False


def download_and_convert():
    print("从 URL 下载并转换")
    
    url = get_input("请输入 CCMZ 文件 URL")
    
    output_file = get_input("请输入输出 MIDI 文件名", default="output.mid")
    
    try:
        downloaded_file = CcmzDownloader.download_ccmz(url)
        
        success = process_ccmz_file(downloaded_file, output_file)
        
        if success:
            print(f"转换完成！MIDI 文件已保存为: {output_file}")
        else:
            print("转换失败")
            
    except Exception as e:
        print(f"处理失败: {str(e)}")


def convert_local_file():
    print("转换本地 CCMZ 文件")
    
    file_path = get_input("请输入 CCMZ 文件路径", default="")
    
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return
    
    default_name = os.path.splitext(os.path.basename(file_path))[0] + ".mid"
    output_file = get_input("请输入输出 MIDI 文件名", default=default_name)
    
    success = process_ccmz_file(file_path, output_file)
    
    if success:
        print(f"转换完成！MIDI 文件已保存为: {output_file}")
    else:
        print("转换失败")


def check_dependencies():
    missing_libs = []
    
    if not MIDO_AVAILABLE:
        missing_libs.append("mido")
    
    if missing_libs:
        print(f"缺少以下库: {', '.join(missing_libs)}")
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
                except Exception as e:
                    print(f"安装 {lib} 失败: {str(e)}")
            
            return check_dependencies()
        else:
            return False
    
    return True


def main():
    print_header()
    
    if not check_dependencies():
        print("继续运行可能会有功能限制")
    
    while True:
        print_menu()
        
        choice = input("请选择 (1-3): ").strip()
        
        if choice == "1":
            download_and_convert()
        elif choice == "2":
            convert_local_file()
        elif choice == "3":
            break
        else:
            print("无效选择，请重新输入")
        
        if choice != "3":
            continue_choice = input("\n是否继续使用其他功能? (y/n): ").lower()
            if continue_choice != 'y':
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("用户中断操作")
    except Exception as e:
        print(f"程序出错: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\n按 Enter 键退出...")
