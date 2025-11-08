"""
FAISS index creation functions for products.
"""
import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import multiprocessing as mp
import time
from typing import Dict
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, BATCH_SIZE, MAX_WORKERS


def get_text_chunks(content, metadata):
    """Create text chunks from content"""
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    split_docs = text_splitter.create_documents(content, metadatas=metadata)
    return split_docs


def create_spec_documents(row, specs_texts):
    """Create spec documents from CSV fields only"""
    spec_docs = []
    
    for st in specs_texts:
        if st and st.strip() and len(st.strip()) > 3:
            meta = {
                "product_code": row["product_code"],
                "source": "csv"
            }
            chunks = get_text_chunks([st], [meta])
            spec_docs.extend(chunks)
    
    return spec_docs


@st.cache_resource
def create_product_index(df, embedding_model):
    """Create FAISS index for product codes"""
    product_docs = []
    for _, row in df.iterrows():
        meta = {"product_code": row["product_code"], "product_name": row["product_name"]}
        text = f"{row['product_code']}"
        chunks = get_text_chunks([text], [meta])
        product_docs.extend(chunks)
    
    return FAISS.from_documents(product_docs, embedding_model)


# Hikvision batch processing functions
def process_product_batch(products_batch, embedding_model):
    """Process a batch of products from CSV only"""
    batch_specs_index = {}
    
    for _, row in products_batch.iterrows():
        product_code = row['product_code']
        print(f"Processing product: {product_code}")
        specs_texts = [
            str(row["product_name"]),
            str(row["description_features"])
        ] + str(row["technical_specifications"]).split("|")
        
        spec_docs = create_spec_documents(row, specs_texts)
        
        if spec_docs:
            batch_specs_index[product_code] = FAISS.from_documents(spec_docs, embedding_model)
            print(f"✓ Created specs index for {product_code} with {len(spec_docs)} documents")
    
    return batch_specs_index


def process_product_batch_pdf(products_batch, embedding_model):
    """Process a batch of products from PDF content"""
    batch_specs_index = {}
    
    for _, row in products_batch.iterrows():
        product_code = row['product_code']
        print(f"Processing product: {product_code}")
        specs_texts = [str(row["pdf_content"])]
        
        spec_docs = create_spec_documents(row, specs_texts)
        
        if spec_docs:
            batch_specs_index[product_code] = FAISS.from_documents(spec_docs, embedding_model)
            print(f"✓ Created specs index for {product_code} with {len(spec_docs)} documents")
    
    return batch_specs_index


@st.cache_resource
def create_enhanced_specs_index_accelerated(df, _embedding_model, batch_size=BATCH_SIZE, max_workers=MAX_WORKERS):
    """Create specs index from CSV only with batch processing for Hikvision"""
    
    if max_workers is None:
        max_workers = min(4, mp.cpu_count())
    
    batches = [df.iloc[i:i+batch_size] for i in range(0, len(df), batch_size)]
    print(f"Processing {len(df)} products in {len(batches)} batches of {batch_size}")
    
    specs_index = {}
    start_time = time.time()
    
    for i, batch in enumerate(batches):
        print(f"\n--- Processing Batch {i+1}/{len(batches)} ---")
        batch_start = time.time()
        
        batch_result = process_product_batch(batch, _embedding_model)
        specs_index.update(batch_result)
        
        batch_time = time.time() - batch_start
        print(f"Batch {i+1} completed in {batch_time:.1f}s")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Total processing time: {total_time:.1f}s for {len(df)} products")
    print(f"⚡ Average: {total_time/len(df):.1f}s per product")
    
    return specs_index


@st.cache_resource
def create_enhanced_specs_index_accelerated_pdf(df, _embedding_model, batch_size=BATCH_SIZE, max_workers=MAX_WORKERS):
    """Create specs index from PDF with batch processing for Hikvision"""
    
    if max_workers is None:
        max_workers = min(4, mp.cpu_count())
    
    batches = [df.iloc[i:i+batch_size] for i in range(0, len(df), batch_size)]
    print(f"Processing {len(df)} products in {len(batches)} batches of {batch_size}")
    
    specs_index = {}
    start_time = time.time()
    
    for i, batch in enumerate(batches):
        print(f"\n--- Processing Batch {i+1}/{len(batches)} ---")
        batch_start = time.time()
        
        batch_result = process_product_batch_pdf(batch, _embedding_model)
        specs_index.update(batch_result)
        
        batch_time = time.time() - batch_start
        print(f"Batch {i+1} completed in {batch_time:.1f}s")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Total processing time: {total_time:.1f}s for {len(df)} products")
    print(f"⚡ Average: {total_time/len(df):.1f}s per product")
    
    return specs_index


# Satel batch processing functions
def process_product_batch_satel(products_batch, embedding_model):
    """Process a batch of products from CSV only for Satel"""
    batch_specs_index = {}
    
    for _, row in products_batch.iterrows():
        product_code = row['product_code']
        print(f"Processing product: {product_code}")
        specs_texts = [
            str(row["product_name"]),
            str(row["description"])
        ] + str(row["features_description"]).split("|") + str(row["technical_specifications"]).split("|") + \
        str(row["documents"]).split("|") + str(row["softwares"]).split("|") + str(row["certificates"]).split("|")
        
        spec_docs = create_spec_documents(row, specs_texts)
        
        if spec_docs:
            batch_specs_index[product_code] = FAISS.from_documents(spec_docs, embedding_model)
            print(f"✓ Created specs index for {product_code} with {len(spec_docs)} documents")
    
    return batch_specs_index


def process_product_batch_pdf_satel(products_batch, embedding_model):
    """Process a batch of products from PDF content for Satel"""
    batch_specs_index = {}
    
    for _, row in products_batch.iterrows():
        product_code = row['product_code']
        print(f"Processing product: {product_code}")
        specs_texts = [str(row["pdf_content"])]
        
        spec_docs = create_spec_documents(row, specs_texts)
        
        if spec_docs:
            batch_specs_index[product_code] = FAISS.from_documents(spec_docs, embedding_model)
            print(f"✓ Created specs index for {product_code} with {len(spec_docs)} documents")
    
    return batch_specs_index


@st.cache_resource
def create_enhanced_specs_index_accelerated_satel(df, _embedding_model, batch_size=BATCH_SIZE, max_workers=MAX_WORKERS):
    """Create specs index from CSV only with batch processing for Satel"""
    
    if max_workers is None:
        max_workers = min(4, mp.cpu_count())
    
    batches = [df.iloc[i:i+batch_size] for i in range(0, len(df), batch_size)]
    print(f"Processing {len(df)} products in {len(batches)} batches of {batch_size}")
    
    specs_index = {}
    start_time = time.time()
    
    for i, batch in enumerate(batches):
        print(f"\n--- Processing Batch {i+1}/{len(batches)} ---")
        batch_start = time.time()
        
        batch_result = process_product_batch_satel(batch, _embedding_model)
        specs_index.update(batch_result)
        
        batch_time = time.time() - batch_start
        print(f"Batch {i+1} completed in {batch_time:.1f}s")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Total processing time: {total_time:.1f}s for {len(df)} products")
    print(f"⚡ Average: {total_time/len(df):.1f}s per product")
    
    return specs_index


@st.cache_resource
def create_enhanced_specs_index_accelerated_pdf_satel(df, _embedding_model, batch_size=BATCH_SIZE, max_workers=MAX_WORKERS):
    """Create specs index from PDF with batch processing for Satel"""
    
    if max_workers is None:
        max_workers = min(4, mp.cpu_count())
    
    batches = [df.iloc[i:i+batch_size] for i in range(0, len(df), batch_size)]
    print(f"Processing {len(df)} products in {len(batches)} batches of {batch_size}")
    
    specs_index = {}
    start_time = time.time()
    
    for i, batch in enumerate(batches):
        print(f"\n--- Processing Batch {i+1}/{len(batches)} ---")
        batch_start = time.time()
        
        batch_result = process_product_batch_pdf_satel(batch, _embedding_model)
        specs_index.update(batch_result)
        
        batch_time = time.time() - batch_start
        print(f"Batch {i+1} completed in {batch_time:.1f}s")
    
    total_time = time.time() - start_time
    print(f"\n🎉 Total processing time: {total_time:.1f}s for {len(df)} products")
    print(f"⚡ Average: {total_time/len(df):.1f}s per product")
    
    return specs_index

