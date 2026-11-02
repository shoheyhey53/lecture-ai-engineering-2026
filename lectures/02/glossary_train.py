model.config.use_cache = False
set_seed(42)
adv_lora = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, bias='none',
    task_type='CAUSAL_LM', target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'])
adv_config = SFTConfig(output_dir=str(ADV_WORK / 'ckpt'), num_train_epochs=3,
    per_device_train_batch_size=4, gradient_accumulation_steps=2,
    learning_rate=2e-4, lr_scheduler_type='cosine', warmup_steps=6,
    logging_steps=10, save_steps=15, save_total_limit=2,
    fp16=False, max_length=512, packing=False, report_to='none', seed=42)
adv_trainer = SFTTrainer(model=model, args=adv_config,
    train_dataset=Dataset.from_list(examples), peft_config=adv_lora, processing_class=tok)
adv_trainer.model.print_trainable_parameters()
start=time.time()
adv_trainer.train()
adv_elapsed=time.time()-start
adv_tuned=adv_trainer.model
adv_tuned.config.use_cache=True
adv_tuned.eval()
adv_tuned.save_pretrained(ADV_WORK / 'adapter')
print('ADV_TRAIN_DONE',round(adv_elapsed,1),'seconds; steps=',adv_trainer.state.global_step)
