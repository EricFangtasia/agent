"""
定时任务调度模块
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

class TaskScheduler:
    """
    定时任务调度器
    """
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.logger = logging.getLogger(__name__)
        self.jobs = {}
    
    def add_interval_job(self, func, seconds: int, job_id: str, **kwargs):
        """
        添加间隔任务
        """
        try:
            job = self.scheduler.add_job(
                func,
                trigger=IntervalTrigger(seconds=seconds),
                id=job_id,
                **kwargs
            )
            self.jobs[job_id] = job
            self.logger.info(f"已添加间隔任务: {job_id}, 间隔: {seconds}秒")
            return job
        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            return None
    
    def add_cron_job(self, func, hour: int, minute: int, job_id: str, **kwargs):
        """
        添加定时任务（按时间点）
        """
        try:
            job = self.scheduler.add_job(
                func,
                trigger='cron',
                hour=hour,
                minute=minute,
                id=job_id,
                **kwargs
            )
            self.jobs[job_id] = job
            self.logger.info(f"已添加定时任务: {job_id}, 时间: {hour:02d}:{minute:02d}")
            return job
        except Exception as e:
            self.logger.error(f"添加任务失败: {e}")
            return None
    
    def remove_job(self, job_id: str):
        """
        移除任务
        """
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            self.logger.info(f"已移除任务: {job_id}")
        except Exception as e:
            self.logger.error(f"移除任务失败: {e}")
    
    def start(self):
        """
        启动调度器
        """
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("定时任务调度器已启动")
    
    def shutdown(self):
        """
        关闭调度器
        """
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("定时任务调度器已关闭")
    
    def get_jobs(self):
        """
        获取所有任务
        """
        return self.scheduler.get_jobs()
    
    def pause_job(self, job_id: str):
        """
        暂停任务
        """
        try:
            self.scheduler.pause_job(job_id)
            self.logger.info(f"已暂停任务: {job_id}")
        except Exception as e:
            self.logger.error(f"暂停任务失败: {e}")
    
    def resume_job(self, job_id: str):
        """
        恢复任务
        """
        try:
            self.scheduler.resume_job(job_id)
            self.logger.info(f"已恢复任务: {job_id}")
        except Exception as e:
            self.logger.error(f"恢复任务失败: {e}")
