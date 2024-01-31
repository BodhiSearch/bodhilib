use bodhilibrs::splitter::RecursiveCharacterTextSplitter;
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use std::{fs, io::Read};

fn recursive_text_splitter(data_folder: &str) {
  let separators = vec!["\n\n".into(), "\n".into(), " ".into(), "".into()];
  let splitter = build_splitter();
  let files = glob::glob(&format!("{}/*.md", data_folder))
    .unwrap()
    .filter_map(|f| f.ok())
    .collect::<Vec<_>>();
  let total_len = 10 * files.len();
  let files = files.into_iter().cycle().take(total_len).collect::<Vec<_>>();
  files.into_iter().for_each(|path| {
    let mut contents = String::new();
    let mut file = fs::File::open(path).unwrap();
    let _ = file.read_to_string(&mut contents).unwrap();
    let _ = splitter.split_text(&contents, separators.clone());
  });
}

fn recursive_text_splitter_rayon(data_folder: &str) {
  let files = glob::glob(&format!("{}/*.md", data_folder))
    .unwrap()
    .filter_map(|f| f.ok())
    .collect::<Vec<_>>();
  let total_len = 10 * files.len();
  let files = files.into_iter().cycle().take(total_len).collect::<Vec<_>>();
  let splitter = build_splitter();
  splitter.split_files(files);
}

fn build_splitter() -> RecursiveCharacterTextSplitter {
  let separators = vec!["\n\n".into(), "\n".into(), " ".into(), "".into()];
  RecursiveCharacterTextSplitter {
    separators: separators.clone(),
    keep_separator: true,
    is_separator_regex: false,
    _strip_whitespace: true,
    _chunk_size: 1000,
    _chunk_overlap: 60,
  }
}

fn criterion_benchmark(c: &mut Criterion) {
  let data = std::env::var("PG_ESSAYS_FOLDER").unwrap();
  c.bench_function("recursive_text_splitter", |b| {
    b.iter(|| recursive_text_splitter(black_box(&data)))
  })
  .bench_function("recursive_text_splitter_rayon", |b| {
    b.iter(|| recursive_text_splitter_rayon(black_box(&data)))
  });
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
