import streamlit as st
import os
import pandas as pd
import random
import base64


@st.cache_resource
def get_default_annotation_data():
    return pd.DataFrame({
        'Text': ['Sample text'],
        'Start time (min)': [0],
        'Start time (sec)': [5],
        'End time (min)': [0],
        'End time (sec)': [10],
    })


@st.cache_resource
def get_default_trimming_data():
    return pd.DataFrame({
        'Start time (min)': [0],
        'Start time (sec)': [5],
        'End time (min)': [0],
        'End time (sec)': [10],
    })


def draw_text_on_video(df, input_mp4_file, output_mp4_file):

    drawtext_strings = []
    for _, row in df.iterrows():
        drawtext_strings.append(f"drawtext=text='{row['Text']}':fontcolor=yellow:fontsize=50:x=(w-text_w)/2:y=h-(text_h*2):box=1:boxcolor=black@0.5:enable='between(t,{row['Start time (min)'] * 60 + row['Start time (sec)']},{row['End time (min)'] * 60 + row['End time (sec)']})'")

    if os.path.exists(output_mp4_file):
        os.remove(output_mp4_file)

    joined_string = ', '.join(drawtext_strings)

    os.system(f"ffmpeg -i {input_mp4_file} -vf \"{joined_string}\" {output_mp4_file}")


def trim_video(df, input_mp4_file, output_mp4_file):

    between_strings = []
    for _, row in df.iterrows():
        between_strings.append(f"between(t,{row['Start time (min)'] * 60 + row['Start time (sec)']},{row['End time (min)'] * 60 + row['End time (sec)']})")

    if os.path.exists(output_mp4_file):
        os.remove(output_mp4_file)

    joined_string = '+'.join(between_strings)

    os.system(f"ffmpeg -i {input_mp4_file} -vf \"select='not({joined_string})',setpts=N/FRAME_RATE/TB\" -af \"aselect='not({joined_string})',asetpts=N/SR/TB\" {output_mp4_file}")


def text_annotation_section():

    st.write('This function allows you to add text overlays to the video.')

    use_existing_annotation_file = st.checkbox('Use existing annotation file')

    input_annotation_file = st.selectbox('Optionally select an input annotation file:', [file for file in os.listdir() if file.endswith('.csv')], disabled=not use_existing_annotation_file)

    if 'random_10_digit_string' not in st.session_state:
        st.session_state['random_10_digit_string'] = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    if 'df_initial_annotations' not in st.session_state:
        st.session_state['df_initial_annotations'] = get_default_annotation_data()
    if st.button('Load initial annotation data'):
        if use_existing_annotation_file:
            st.session_state['df_initial_annotations'] = pd.read_csv(input_annotation_file)
        else:
            st.session_state['df_initial_annotations'] = get_default_annotation_data()
        st.session_state['random_10_digit_string'] = ''.join([str(random.randint(0, 9)) for _ in range(10)])

    df = st.session_state['df_initial_annotations']

    process_button_text = 'Create MP4 with text overlay'

    process_function = draw_text_on_video

    st.write('**NOTE**: Do not use double quotes in the text in the table below. Single quotes are fine though they won\'t actually show up.')

    return df, process_button_text, process_function


def trimming_section():

    st.write('This function allows you to trim the the video.')

    use_existing_trimming_file = st.checkbox('Use existing trimming file')

    input_trimming_file = st.selectbox('Optionally select an input trimming file:', [file for file in os.listdir() if file.endswith('.csv')], disabled=not use_existing_trimming_file)

    if 'random_10_digit_string' not in st.session_state:
        st.session_state['random_10_digit_string'] = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    if 'df_initial_trimmings' not in st.session_state:
        st.session_state['df_initial_trimmings'] = get_default_trimming_data()
    if st.button('Load initial annotation data'):
        if use_existing_trimming_file:
            st.session_state['df_initial_trimmings'] = pd.read_csv(input_trimming_file)
        else:
            st.session_state['df_initial_trimmings'] = get_default_trimming_data()
        st.session_state['random_10_digit_string'] = ''.join([str(random.randint(0, 9)) for _ in range(10)])

    df = st.session_state['df_initial_trimmings']

    process_button_text = 'Create trimmed MP4'

    process_function = trim_video

    return df, process_button_text, process_function


def main():

    st.set_page_config(page_title="Create GIF", page_icon=":camera:", layout="wide")

    cols = st.columns([0.45, 0.3, 0.25])

    with cols[0]:

        st.header('Input video')

        input_mp4_file = st.selectbox('Select the input video file:', [file for file in os.listdir() if file.endswith('.mp4')])

        st.video(input_mp4_file)

    with cols[1]:

        st.header('Processing')

        if 'function' not in st.session_state:
            st.session_state['function'] = 'Text annotation'
        function = st.selectbox('Select processing function:', ['Text annotation', 'Trimming'], key='function')

        if function == 'Text annotation':

            df, process_button_text, process_function = text_annotation_section()

        elif function == 'Trimming':

            df, process_button_text, process_function = trimming_section()

        df_edited = st.data_editor(df, num_rows='dynamic', key=st.session_state['random_10_digit_string'])

        output_mp4_file = st.text_input('Enter the output video file name:', 'output.mp4')

        if st.button(process_button_text):

            process_function(df_edited, input_mp4_file, output_mp4_file)

            st.success(f"Video file {output_mp4_file} created successfully!")

    with cols[2]:

        st.header('Output video')

        if os.path.exists(output_mp4_file):
            st.video(output_mp4_file)

        if st.button('Create GIF from video'):
            output_gif_file = output_mp4_file.replace('.mp4', '.gif')
            if os.path.exists(output_gif_file):
                os.remove(output_gif_file)
            os.system(f"ffmpeg -i {output_mp4_file} {output_gif_file}")
            st.success(f"GIF file {output_gif_file} created successfully!")
            st.session_state['output_gif_file'] = output_gif_file

        with st.expander('View GIF'):
            if 'output_gif_file' in st.session_state and os.path.exists(st.session_state['output_gif_file']):
                file_ = open(st.session_state['output_gif_file'], "rb")
                contents = file_.read()
                data_url = base64.b64encode(contents).decode("utf-8")
                file_.close()

                st.markdown(
                    f'<img src="data:image/gif;base64,{data_url}" alt="animated gif">',
                    unsafe_allow_html=True,
                )


if __name__ == '__main__':
    main()
