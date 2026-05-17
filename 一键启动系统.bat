@echo off
chcp 65001 >nul
title 电商知识图谱智能客服系统 - 启动中心
echo =======================================================
echo         电商知识图谱智能客服系统 - 一键启动脚本
echo =======================================================
echo.
echo 正在为您同时启动 【前端界面】 和 【大模型后台引擎】...
echo.

:: 启动大模型后台 (新建窗口)
echo [1/2] 正在拉起本地大模型 Qwen (加载到显存大约需要30-60秒)...
start "大模型后台引擎" cmd /k "cd /d %~dp0LLaMA-Factory && call ..\.venv\Scripts\activate.bat && set PYTHONPATH=%~dp0LLaMA-Factory\src && set HF_ENDPOINT=https://hf-mirror.com && echo ===================================== && echo 正在加载大模型到显存，加载期间请勿关闭此窗口 && echo 当出现【Uvicorn running on http://0.0.0.0:8000】代表已就绪！ && echo ===================================== && python -m llamafactory.cli api --model_name_or_path C:\Users\kai\.cache\huggingface\hub\models--Qwen--Qwen2.5-1.5B-Instruct\snapshots\989aa7980e4cf806f80c7fef2b1adb7bc71aa306 --adapter_name_or_path saves\Qwen2.5-1.5B-Instruct\lora\train_2026-03-15-21-32-40 --template qwen --finetuning_type lora --quantization_bit 4"

:: 等待2秒
timeout /t 2 /nobreak >nul

:: 启动前端控制台 (新建窗口)
echo [2/2] 正在启动 Streamlit 前端数据看板...
start "前端用户界面" cmd /k "cd /d %~dp0 && call .venv\Scripts\activate.bat && echo ===================================== && echo 正在为您打开网页，请不要关闭此黑色终端 && echo ===================================== && streamlit run app.py"

echo.
echo =======================================================
echo 部署指令已全部发出！
echo 默认浏览器将自动打开系统界面 ( http://localhost:8501 )
echo.
echo 注意：
echo 1. 网页右下角的【系统状态】会实时检测大模型是否成功在线。
echo 2. 在它显示 “🟢 已就绪” 之前，请不要点击分析按钮。
echo =======================================================
pause
