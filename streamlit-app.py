# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger

from pypdf import PdfWriter, PdfReader, Transformation
import io
from reportlab.pdfgen.canvas import Canvas

LOGGER = get_logger(__name__)

def create_annotated_pdf(text: str, pagesize, rotate_angle):
#   page_to_merge = [0, 1, 4] #Refers to the First page of PDF 
    xcoor = pagesize[0] - 40 #To be changed according to your pdf
    ycoor = 40 #To be changed according to your pdf

    ycoor = float(pagesize[1]) - ycoor
    packet = io.BytesIO()
    c = Canvas(packet,pagesize=pagesize)
    #   c.setFillColorRGB(1,0,0) #choose your font colour
    c.setFont("Helvetica", 15) #choose your font type and font size
    c.drawRightString(xcoor, ycoor, text)
    c.save()
    packet.seek(0)
    overlay_pdf = PdfReader(packet)
    overlay = overlay_pdf.pages[0]
    overlay.add_transformation(Transformation().
                        rotate(rotate_angle))
                        # .
                        # translate(float(overlay.mediabox.width/2), 0))
    return overlay_pdf


def annotate_pdf_file(pdf_source, names: list):
    input_pdf = PdfReader(pdf_source)
    page_count = len(input_pdf.pages)
    inputpdf_page_to_be_merged = input_pdf.pages[0]
    pagesize=(inputpdf_page_to_be_merged.mediabox.width,inputpdf_page_to_be_merged.mediabox.height)
    annotations = {n: create_annotated_pdf(n, pagesize, inputpdf_page_to_be_merged.get('/Rotate') or 0) for n in names}
    pdf_sources = {n: PdfReader(pdf_source) for n in names}

    output = PdfWriter()
    for PAGE in range(page_count):
        for n in names:
            source_pdf = pdf_sources[n]
            overlay = annotations[n]
            source_page = source_pdf.pages[PAGE]
            source_page.merge_page(overlay.pages[0])
            output.add_page(source_page)

    outputStream = io.BytesIO()
    output.write(outputStream)
    return outputStream.getvalue()


def run():
    st.set_page_config(
        page_title="PDF Annotation",
        page_icon="👋",
    )

    st.write("# PDF Annotation")

    st.markdown(
        """
        Thực hiện annotate và duplicate mỗi trang trong file PDF với các dòng text được input.
    """
    )

    pdf_data = None
    with st.form('upload_form'):
        uploaded_pdf = st.file_uploader(label='Upload PDF file', accept_multiple_files=False, type='pdf')
        names = st.text_area(label='Nhập tên cần dán lên file PDF. Mỗi dòng cho 1 tên', placeholder='Kitty\nMicky')
        submitted =st.form_submit_button('Submit')
        if submitted:
            if uploaded_pdf is None:
                st.write('Must select PDF file first')
                return
            if not names:
                st.write('Must input names')
                return
            name_list = names.splitlines()
            pdf_data = annotate_pdf_file(uploaded_pdf, name_list)

    if pdf_data:
        st.write('Bấm nút download phía dưới để download kết quả')
        st.download_button('Download PDF', data=pdf_data, file_name='result.pdf', mime='application/pdf')


if __name__ == "__main__":
    run()
