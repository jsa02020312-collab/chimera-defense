# Get Started (from this directory)
\* MINJA is implemented on top of the [RAP (Retrieval-Augmented Planning)](https://github.com/PanasonicConnect/rap) agent framework and the [WebShop](https://github.com/princeton-nlp/WebShop) environment.

1. Create conda environment
```bash
conda create -n rap python=3.10 -y
conda activate rap
```

2. Install OpenJDK

```bash
conda install -c conda-forge openjdk=21 -y
```

3. Install other dependencies
```bash
pip install -r requirements.txt
```



4. Create ```OpenAI_api_key.txt``` under this directory and put the prepared OpenAI API key in it. 

# Setup WebShop

**⚠️ Important:** Open a new terminal and run. (Note: Stop/terminate and restart the webserver before each experiment.)
1. According to [WebShop](https://github.com/princeton-nlp/WebShop?tab=readme-ov-file#-setup), set up the webshop environment (choose ```./setup.sh -d all```) and download the datasets.
2. Launch the ```webshop``` webpage:

```bash
cd webshop
./run_dev.sh
```



# Running MINJA on RAP Agent


MINJA on RAP Agent supports configurable adversarial settings defined by a triple (victim, target, price).
Users can specify these parameters via command-line arguments.
```bash
conda activate rap
```
Example:

```bash
python minja.py \
  --victim toothbrush \
  --target "DenTek Professional Oral Care Kit with DenTek Triple Clean Advanced Clean Floss Picks" \
  --target_price 20.0 \
  --inject_num 15 \
  --num_benign 50 \
  --test_num 30 \
  --model_name gpt-4o
```

The complete list of predefined victim–target–target_price configurations is available in:
```bash
victim_target_pair/victim_target.json
```

