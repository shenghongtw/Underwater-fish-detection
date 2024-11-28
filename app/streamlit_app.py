import os
import glob
from PIL import Image
import streamlit as st
from subprocess import call
import subprocess


def main():
    new_title = '<p style="font-size: 42px;">歡迎來到魚類檢測應用程式！</p>'
    read_me_0 = st.markdown(new_title, unsafe_allow_html=True)

    read_me = st.markdown("""
    本專案使用 Streamlit 建立，以展示 YoloV7 模型
    """
                          )
    st.sidebar.title("選擇活動")
    choice = st.sidebar.selectbox(
        "模式", ("關於", "魚類檢測（圖片）", "魚類檢測（影片）"))
    # ["顯示說明","地標識別","顯示原始碼", "關於"]

    if choice == "魚類檢測（圖片）":
        read_me_0.empty()
        read_me.empty()

        upload_image()

    elif choice == "魚類檢測（影片）":
        upload_video()

    elif choice == "關於":
        print()


def upload_image():

    st.title('圖片中的魚類檢測')
    st.subheader("""
    上傳一張有魚的圖片，讓 YoloV7 檢測魚類....
    """)
    file = st.file_uploader('上傳圖片', type=['jpg', 'png', 'jpeg'])
    if file != None:
        placeholder = st.empty()
        img1 = Image.open(file)
        img1.save("source.jpg")
        placeholder.image(img1, caption="已上傳圖片")
        # 修改按鈕的回調方式
        if st.button("檢測魚類"):
            detect_image(placeholder)


def detect_image(placeholder):
    """檢測、儲存並載入來源圖片中的魚類

    Args:
        placeholder (_type_): st.empty()
    """
    
    with st.spinner('檢測中 🐟 🐠 🦈 🐡...'):
        # 修正路徑，使用絕對路徑
        detect_script = os.path.join(os.getcwd(), "yolov7", "detect.py")
        weights_path = os.path.join(os.getcwd(), "weights", "best.pt")
        
        call(["python", detect_script, "--weights", weights_path,
              "--conf-thres", "0.1", "--source", "source.jpg", "--no-trace",
              "--exist-ok", "--project", ".", "--name", "detection"])

        # 修改檢測結果的路徑
        try:
            detected_img = glob.glob("detection/*.jpg")[0]
            placeholder.empty()
            img = Image.open(detected_img)
            placeholder.image(img, caption="魚類檢測")
        except IndexError:
            st.error("檢測過程中發生錯誤，請重試")


def upload_video():
    st.title('影片中的魚類檢測')
    st.subheader("""
    上傳一段有魚的影片，讓 YoloV7 檢測魚類....
    """)
    
    file = st.file_uploader('上傳影片', type=['mp4', 'avi', 'mov'])
    if file is not None:
        # 保存上傳的影片
        with open("source_video.mp4", "wb") as f:
            f.write(file.read())
        
        # 顯示原始影片
        st.video("source_video.mp4")
        
        if st.button("檢測魚類"):
            detect_video()


def detect_video():
    """檢測影片中的魚類"""
    
    with st.spinner('檢測中 🐟 🐠 🦈 🐡...'):
        # 設置路徑
        detect_script = os.path.join(os.getcwd(), "yolov7", "detect.py")
        weights_path = os.path.join(os.getcwd(), "weights", "best.pt")
        
        # 添加取消按鈕
        stop_button = st.empty()
        if stop_button.button("取消檢測"):
            st.stop()
        
        # 顯示預估時間
        st.info("視頻長度越長，處理時間越久，請耐心等待...")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # 運行檢測
            process = subprocess.Popen(
                ["python", detect_script, 
                "--weights", weights_path,
                "--conf-thres", "0.1", 
                "--source", "source_video.mp4", 
                "--no-trace",
                "--exist-ok", 
                "--project", ".", 
                "--name", "detection"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # 更新進度（基於輸出）
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    # 從輸出中解析進度（需要修改 YOLOv7 的輸出格式）
                    if "frame" in output:
                        try:
                            progress = float(output.split("%")[0].split()[-1])
                            progress_bar.progress(int(progress))
                            status_text.text(f"處理進度：{int(progress)}%")
                        except:
                            pass
            
            # 修改檢測結果的處理
            try:
                detected_video = glob.glob("detection/*.mp4")[0]
                
                if not os.path.exists(detected_video):
                    st.error(f"未找到處理後的文件: {detected_video}")
                    return
                
                # 使用 ffmpeg 重新編碼影片，確保瀏覽器相容性
                output_video = "detection/converted_output.mp4"
                ffmpeg_cmd = [
                    'ffmpeg', '-i', detected_video,
                    '-vcodec', 'h264',
                    '-acodec', 'aac',
                    '-strict', '-2',
                    '-y',  # 覆寫現有檔案
                    output_video
                ]
                
                subprocess.run(ffmpeg_cmd, check=True)
                
                # 讀取轉換後的影片
                with open(output_video, 'rb') as video_file:
                    video_bytes = video_file.read()
                    st.video(video_bytes)
                st.success("檢測完成！")
                
                # 清理轉換後的檔案
                try:
                    os.remove(output_video)
                except OSError:
                    pass
                
            except IndexError:
                st.error("無法找到處理後的影片文件")
            except subprocess.CalledProcessError:
                st.error("影片轉換失敗")
            except Exception as e:
                st.error(f"播放影片時發生錯誤: {str(e)}")
                
            # 清理暫存檔案
            try:
                os.remove("source_video.mp4")
            except OSError as e:
                st.warning(f"清理暫存檔案時發生錯誤: {str(e)}")
            
        except Exception as e:
            st.error(f"檢測過程中發生錯誤: {str(e)}")
        finally:
            # 清理進度顯示
            progress_bar.empty()
            status_text.empty()
            stop_button.empty()


if __name__ == '__main__':
    main()
