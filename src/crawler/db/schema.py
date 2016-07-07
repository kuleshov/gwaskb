from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer, Float, Boolean, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy import func

from __init__ import Base, engine

# ----------------------------------------------------------------------
# Database models

class SNP(Base):
  __tablename__ = 'snps'
  id = Column( Integer, primary_key=True, nullable=False, autoincrement=True)
  rs_id           = Column( Integer, nullable=False, unique=True )
  interest        = Column( Integer )
  ref             = Column( String(50) )
  chrom           = Column( Integer )
  position        = Column( Integer )
  gene            = Column( String(50) )
  omim            = Column( Boolean )
  pharmgkb        = Column( Boolean )

class Phenotype(Base):
  __tablename__ = 'phenotypes'
  id = Column( Integer, primary_key=True, nullable=False, autoincrement=True)
  name            = Column( String(1000), nullable=False )
  category        = Column( String(100) ) # disease, drug
  source          = Column( String(100), nullable=False ) # snpedia, gwas_catalog
  synonyms        = Column( String(1000) )
  ontology_ref    = Column( String(1000) )
  misc            = Column( String(1000) )

class Association(Base):
  __tablename__ = 'associations'
  id = Column( Integer, primary_key=True, nullable=False, autoincrement=True)
  allele          = Column( String(10) )
  genotype        = Column( String(10) )
  repute          = Column( String(10) )
  description     = Column( String(100) )
  magnitude       = Column( Float )
  pvalue          = Column( Float )
  oddsratio       = Column( Float )
  beta            = Column( Float )
  beta_params     = Column( String(100) )
  freq            = Column( Float )
  population      = Column( String(100) )
  source          = Column( String(1000) ) # snpedia, gwas_catalog, extracted
  controls        = Column( Integer )
  cases           = Column( Integer )
  snp_id          = Column( Integer, ForeignKey('snps.id') )
  phenotype_id    = Column( Integer, ForeignKey('phenotypes.id') )
  paper_id        = Column( Integer, ForeignKey('papers.id') )
  snp             = relationship('SNP')
  phenotype       = relationship('Phenotype')
  paper           = relationship('Paper')

class Paper(Base):
  __tablename__ = 'papers'
  id = Column( Integer, primary_key=True, nullable=False, autoincrement=True)
  pubmed_id       = Column( Integer, nullable=False, unique=True )
  pmc_id          = Column( Integer )
  authors         = Column( String(1000) )
  journal         = Column( String(1000) )
  open_access     = Column( Boolean )
  snpedia_open    = Column( Boolean )
  title           = Column( String(1000) )
  abstract        = Column( String(10000) )
  pdf_id          = Column( Integer, ForeignKey('files.id') )
  pdf             = relationship('File', primaryjoin='Paper.pdf_id==File.id', post_update=True)
  files           = relationship('File', primaryjoin='Paper.id==File.paper_id')

class File(Base):
  __tablename__ = 'files'
  id = Column( Integer, primary_key=True, nullable=False, autoincrement=True)
  paper_id        = Column(Integer, ForeignKey('papers.id'))
  filename        = Column( String(1000) ) # relative to db_dir
  format          = Column( String(5) ) # pdf, excel, tgz

class SnpediaEvidence(Base):
  __tablename__ = 'snpedia_evidence'
  id = Column( Integer, primary_key=True, nullable=False, autoincrement=True)
  snp_id          = Column( Integer, ForeignKey('snps.id') )
  paper_id        = Column( Integer, ForeignKey('papers.id') )
  snp             = relationship('SNP')
  paper           = relationship('Paper')
  snpedia_open    = Column( Boolean )
  automatic       = Column( Boolean )

# ----------------------------------------------------------------------------

def init_db():
  Base.metadata.create_all(bind=engine)