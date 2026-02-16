# Code — Chapter 06 (Planning)

Create a per-chapter virtualenv and install dependencies:

```bash
cd code
./setup_venv.sh chapter_06
source chapter_06/.venv/bin/activate

# Copy example env and update secrets
cp code/.env.example code/chapter_06/.env
# edit code/chapter_06/.env with your secrets
```

Place runnable examples in this folder. Keep heavy dependencies minimal until you need provider-specific integrations.
